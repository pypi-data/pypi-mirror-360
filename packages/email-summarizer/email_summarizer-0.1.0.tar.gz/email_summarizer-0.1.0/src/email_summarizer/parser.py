# src/backend/parser.py

import email
import email.message
import re
from typing import List, Dict

def _get_body(msg: email.message.Message) -> str:
    """
    Extract the plain-text body from an email.message.Message.
    """
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                charset = part.get_content_charset() or "utf-8"
                return part.get_payload(decode=True).decode(charset, errors="replace")
    else:
        charset = msg.get_content_charset() or "utf-8"
        return msg.get_payload(decode=True).decode(charset, errors="replace")
    return ""

def parse_email(raw_email: str) -> List[Dict[str, str]]:
    """
    If this looks like a complete MIME email (e.g. starts with MIME-Version:),
    parse it as a single message. Otherwise treat it as a threaded dump and split
    on lines starting with "From:".
    """
    # Detect a full .eml style email
    if re.match(r'^\s*MIME-Version:', raw_email):
        msg = email.message_from_string(raw_email)
        return [{
            "sender":  msg.get("From", "").strip(),
            "date":    msg.get("Date", "").strip(),
            "subject": msg.get("Subject", "").strip(),
            "body":    _get_body(msg).strip()
        }]

    # Naive thread-split fallback
    chunks = re.split(r'(?m)^From: ', raw_email)
    messages = []
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        raw = "From: " + chunk
        msg = email.message_from_string(raw)
        messages.append({
            "sender":  msg.get("From", "").strip(),
            "date":    msg.get("Date", "").strip(),
            "subject": msg.get("Subject", "").strip(),
            "body":    _get_body(msg).strip()
        })

    # Threads often newest-first; remove reverse if you want natural order
    return messages


def parse_linkedin(html: str) -> str:
    """
    Very basic HTML→text conversion: strip tags and collapse whitespace.
    You can swap in html2text or BeautifulSoup later if needed.
    """
    # strip tags
    text = re.sub(r"<[^>]+>", "", html)
    # collapse multiple spaces/newlines
    text = re.sub(r"\s+", " ", text).strip()
    return text