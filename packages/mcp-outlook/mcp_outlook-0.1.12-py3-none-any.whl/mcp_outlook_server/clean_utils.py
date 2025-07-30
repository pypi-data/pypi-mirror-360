import re, logging, html, html2text, unicodedata
from bs4 import BeautifulSoup
from functools import wraps
from typing import Any, List, Dict
from .format_utils import get_date, get_sender_info, get_message_attribute

logger = logging.getLogger(__name__)

def exception_handler(default_return=""):
    # Handle exceptions.
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                return default_return if args and args[0] is None else (args[0] if args else default_return)
        return wrapper
    return decorator

@exception_handler()
def clean_text(text, aggressive=False):
    # Clean and normalize text.
    if not text: 
        return ""
    
    text = re.sub(r'[\ufeff\u200b-\u200f\u2028\u2029\u202a-\u202e\x00-\x09\x0B\x0C\x0E-\x1F\x7F]', '', text) # Remove invisible/control chars.
    
    if aggressive:
        text = re.sub(r'[\u2060-\u2064\u206A-\u206F\u00AD\u034F]', '', text) # Remove additional formatting chars.
        text = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text) # Remove ANSI escape sequences.
        text = re.sub(r'[^\w\s\.,!\?;:\-\'"áéíóúñüÁÉÍÓÚÑÜ¿¡@]', ' ', text) # Remove non-standard punctuation, allowing @.
    
    text = re.sub(r'\s+', ' ', text) # Normalize whitespace.
    text = re.sub(r'^ +| +$', '', text, flags=re.MULTILINE) # Trim leading/trailing spaces per line.
    
    lines = text.split('\n')
    # Remove lines with only special characters or empty after strip.
    clean_lines = [line for line in lines if line.strip() and not re.match(r'^[\s\-\*\+\=\|\_\#\~\`]*$', line.strip())]
    text = '\n'.join(clean_lines)
    return unicodedata.normalize('NFC', text)

@exception_handler()
def html_to_text(html_content):
    # Convert HTML to plain text.
    if not html_content: 
        return ""
    
    try: html_content = html.unescape(html_content) # Decode HTML entities.
    except Exception as e: logger.debug(f"Error unescaping HTML: {e}")

    soup = BeautifulSoup(html_content, 'html.parser')
    
    for tag_name in ['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript', 'form', 'input', 'button', 'meta', 'link']:
        for tag in soup.find_all(tag_name):
            tag.decompose() # Remove unwanted elements.
    
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_tables = True
    h.ignore_emphasis = True
    h.body_width = 0
    h.unicode_snob = True
    h.ul_item_mark = ' ' 
    h.emphasis_mark = ''
    h.single_line_break = True

    text = h.handle(str(soup))
    
    text = re.sub(r'<[^>]+>', '', text) # Remove any remaining HTML tags.
    text = re.sub(r'\!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)|\\[cid:[^\]]*\\]|\\[[^\]]*\\]', '', text, flags=re.IGNORECASE) # Remove markdown images/links, cids, brackets.
    text = re.sub(r'\|[\s\-\|]*\||^\s*\||\|\s*$|\s*\|\s*', ' ', text, flags=re.MULTILINE) # Clean table remnants.
    text = re.sub(r'[\*\_]{2,}|[\#\=\-\+]{2,}', '', text) # Remove excessive formatting chars.
    text = re.sub(r'[ \t]+', ' ', text) # Normalize spaces/tabs.
    text = re.sub(r'\n\s*\n', '\n\n', text) # Ensure max one blank line.
    text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE) # Trim leading/trailing whitespace from each line.
    
    # Remove empty lines or lines with only residual non-alphanumeric characters.
    lines = text.split('\n')
    clean_lines = [line for line in lines if line.strip() and re.search(r'[a-zA-Z0-9]', line)]
    text = '\n'.join(clean_lines)
    
    return text.strip()

@exception_handler()
def process_text(text):
    # Process text for cleaner output.
    if not text: 
        return ""
    
    url_pattern_list = [ # More comprehensive TLD list.
        r'https?://[^\s\n<>()\[\]]+', r'ftp://[^\s\n<>()\[\]]+', r'www\.[^\s\n<>()\[\]]+',
        r'mailto:[^\s\n<>()\[\]]+', r'tel:[+\d\s\(\)\-]+'
    ]
    for pattern in url_pattern_list: 
        text = re.sub(pattern, '', text, flags=re.IGNORECASE) # Remove URLs and links.

    text = re.sub(r'[•·▪▫◦‣⁃]', '-', text) # Normalize bullet points.
    text = re.sub(r'[\"\'`‘’“”«»]', '"', text) # Normalize quotes.
    text = re.sub(r'[–—―]', '-', text) # Normalize dashes.
    text = re.sub(r'…', '...', text) # Normalize ellipsis.
    text = re.sub(r'©|®|™', '', text) # Remove copyright/trademark symbols.

    lines = text.split('\n')
    unique_lines, prev_line_hash = [], None
    for line in lines: # Remove duplicate consecutive lines and very short/artifact lines.
        stripped_line = line.strip()
        current_hash = hash(stripped_line)
        if stripped_line and re.search(r'[a-zA-Z0-9]', stripped_line) and current_hash != prev_line_hash and len(stripped_line) > 1:
            unique_lines.append(stripped_line)
            prev_line_hash = current_hash
    result = '\n'.join(unique_lines)
    
    # Eliminar saltos de línea y espacios excesivos
    result = re.sub(r'\n{3,}', '\n\n', result)
    result = re.sub(r'[ \t]{2,}', ' ', result).strip()
    lines = result.split('\n')
    result = '\n'.join([line for line in lines if line.strip() and re.search(r'[a-zA-Z0-9]', line)])
    # Corte agresivo de boilerplate/disclaimers
    result = remove_email_noise(result)
    return result.strip()

def remove_email_noise(text: str) -> str:
    # Trunca el texto en el primer patrón típico de ruido/boilerplate/disclaimer.
    noise_patterns = [
        r'(?i)\b(confidential|disclaimer|privileged|legal notice|aviso legal|important notice)\b.{0,500}',
        r'(?i)\b(this email and any files|this message and any attachments|the information contained in this email)\b.{0,500}',
        r'(?i)\b(unsubscribe|manage preferences|privacy policy|terms of service|view in browser|view as a web page)\b.{0,300}',
        r'(?i)\b(copyright|all rights reserved|© \d{4})\b.{0,200}',
        r'(?i)\b(sent from my |enviado desde mi |powered by |get the app)\b.{0,100}',
        r'(?i)---------- Forwarded message ----------|From: .* Sent: .* To: .* Subject: .*'
    ]
    for pattern in noise_patterns:
        match = re.search(pattern, text)
        if match and match.start() > len(text) * 0.6: # Truncate if disclaimer is in the latter part.
            return text[:match.start()].strip()
    return text

def clean_email_content(html_content, aggressive=True):
    # Clean email content (HTML or plain).
    if not html_content: return ""
    try:
        text_from_html = html_to_text(html_content)
        cleaned_text = clean_text(text_from_html, aggressive=aggressive)
        processed_text = process_text(cleaned_text)
        return re.sub(r'\n{3,}', '\n\n', processed_text).strip()
    except Exception as e:
        logger.error(f"Error in email cleaning pipeline: {e}. Falling back.")
        try: # Fallback strategy.
            fallback_text = html_to_text(html_content) 
            if fallback_text: fallback_text = process_text(fallback_text)
            text_content = fallback_text or html_content
            text_content = re.sub(r'<[^>]+>', ' ', text_content)
            return re.sub(r'\s+', ' ', text_content).strip()
        except Exception as fallback_e: # Absolute last resort.
            logger.error(f"Error in fallback email cleaning: {fallback_e}")
            text = re.sub(r'<[^>]+>', ' ', html_content)
            return re.sub(r'\s+', ' ', text).strip()

def format_email_structured(message: Any) -> Dict[str, Any]:
    # Format email into a structured dictionary.
    if not message:
        return {"remitente": "Desconocido", "fecha": "Desconocida", "copiados": [], "asunto": "Sin asunto", "resumen": "No disponible", "cuerpo": "Contenido no disponible", "id": "Desconocido"}
    sender_name, sender_email = get_sender_info(message)
    fecha_raw = get_date(message)
    fecha = "Desconocida" if fecha_raw == "Unknown" else fecha_raw
    remitente = f"{sender_name} <{sender_email}>" if sender_name else (sender_email or "Desconocido")
    copiados = []
    try:
        for cc_type in ['ccRecipients', 'bccRecipients']:
            recipients = get_message_attribute(message, [cc_type])
            if recipients:
                for recipient in recipients:
                    if hasattr(recipient, 'emailAddress'):
                        email_addr = recipient.emailAddress
                        name = get_message_attribute(email_addr, ['name'], "")
                        email = get_message_attribute(email_addr, ['address'], "")
                        if email: copiados.append(f"{name} <{email}>" if name else email)
    except Exception: pass
    asunto = get_message_attribute(message, ['subject'], "Sin asunto")
    cuerpo_raw, content_type = "", "text"
    try:
        if hasattr(message, 'body') and message.body:
            body = message.body
            # Compatibilidad: puede ser dict o tener atributos
            if isinstance(body, dict):
                cuerpo_raw = body.get('content', "")
                content_type = body.get('contentType', body.get('content_type', 'text')).lower()
            else:
                cuerpo_raw = getattr(body, 'content', "")
                content_type = getattr(body, 'contentType', getattr(body, 'content_type', 'text')).lower()
    except Exception: pass
    cuerpo = clean_email_content(cuerpo_raw, aggressive=True) if content_type == 'html' else process_text(clean_text(cuerpo_raw or "", aggressive=True))
    if not cuerpo.strip(): cuerpo = "Contenido no disponible"
    if cuerpo == "Contenido no disponible": resumen = "No disponible"
    else:
        resumen_text = re.sub(r'\s+', ' ', cuerpo.replace('\n', ' ')).strip()
        resumen = (resumen_text[:150] + "..." if len(resumen_text) > 150 else resumen_text)
        if not resumen.strip(): resumen = "Contenido procesado, resumen no extraíble."
    message_id = get_message_attribute(message, ['id'], "Desconocido")
    return {"remitente": remitente, "fecha": fecha, "copiados": copiados, "asunto": asunto, "resumen": resumen, "cuerpo": cuerpo, "id": message_id}

def format_emails_list_structured(messages: List[Any]) -> List[Dict[str, Any]]:
    # Format a list of emails into structured dictionaries.
    return [format_email_structured(msg) for msg in messages] if messages else []

def format_email_structured_no_body(message: Any) -> Dict[str, Any]:
    # Fromat email into a structured dictionary without body content.
    if not message:
        return {"remitente": "Desconocido", "fecha": "Desconocida", "copiados": [], "asunto": "Sin asunto", "resumen": "No disponible", "cuerpo": "Contenido no disponible", "id": "Desconocido"}
    sender_name, sender_email = get_sender_info(message)
    fecha_raw = get_date(message)
    fecha = "Desconocida" if fecha_raw == "Unknown" else fecha_raw
    remitente = f"{sender_name} <{sender_email}>" if sender_name else (sender_email or "Desconocido")
    copiados = []
    try:
        for cc_type in ['ccRecipients', 'bccRecipients']:
            recipients = get_message_attribute(message, [cc_type])
            if recipients:
                for recipient in recipients:
                    if hasattr(recipient, 'emailAddress'):
                        email_addr = recipient.emailAddress
                        name = get_message_attribute(email_addr, ['name'], "")
                        email = get_message_attribute(email_addr, ['address'], "")
                        if email: copiados.append(f"{name} <{email}>" if name else email)
    except Exception: pass
    asunto = get_message_attribute(message, ['subject'], "Sin asunto")
    resumen = get_message_attribute(message, ['bodyPreview'], "No disponible")
    cuerpo = "Contenido no disponible"
    message_id = get_message_attribute(message, ['id'], "Desconocido")
    return {"remitente": remitente, "fecha": fecha, "copiados": copiados, "asunto": asunto, "resumen": resumen, "cuerpo": cuerpo, "id": message_id}

def format_emails_list_structured_no_body(messages: List[Any]) -> List[Dict[str, Any]]:
    return [format_email_structured_no_body(msg) for msg in messages] if messages else []
