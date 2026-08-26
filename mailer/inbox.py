import email
import imaplib
import os
from email.header import decode_header
from email.message import Message
from email.utils import parseaddr

from dotenv import load_dotenv

load_dotenv()

IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
IMAP_MAILBOX = os.getenv("IMAP_MAILBOX", "INBOX")
PROMOTIONAL_SUBJECT_WORDS = {
    "sale",
    "deal",
    "discount",
    "offer",
    "promotion",
    "promotional",
    "newsletter",
    "unsubscribe",
}


def _decode_header_value(value):
    if not value:
        return ""

    parts = []
    for text, encoding in decode_header(value):
        if isinstance(text, bytes):
            parts.append(text.decode(encoding or "utf-8", errors="replace"))
        else:
            parts.append(text)
    return "".join(parts)


def _text_body(message: Message):
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in str(
                part.get("Content-Disposition", "")
            ).lower():
                return part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", errors="replace"
                )
        return ""

    payload = message.get_payload(decode=True)
    if not payload:
        return ""
    return payload.decode(message.get_content_charset() or "utf-8", errors="replace")


def is_promotional(message: Message):
    subject = _decode_header_value(message.get("Subject", "")).lower()
    headers = " ".join(
        str(message.get(header, ""))
        for header in ("List-Unsubscribe", "List-Id", "Precedence", "X-Mailer")
    ).lower()
    body = _text_body(message).lower()

    if message.get("List-Unsubscribe") or message.get("Precedence", "").lower() in {
        "bulk",
        "list",
        "junk",
    }:
        return True

    if any(word in subject.split() for word in PROMOTIONAL_SUBJECT_WORDS):
        return True

    return "unsubscribe" in headers or "unsubscribe" in body


def read_unread_messages():
    username = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_APP_PASSWORD")
    if not username or not password:
        raise ValueError("Email credentials are missing in .env")

    messages = []
    with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as mailbox:
        mailbox.login(username, password)
        mailbox.select(IMAP_MAILBOX)
        status, data = mailbox.search(None, "UNSEEN")
        if status != "OK":
            raise RuntimeError("Could not search for unread email")

        for uid in data[0].split():
            status, fetched = mailbox.fetch(uid, "(RFC822)")
            if status != "OK" or not fetched or not isinstance(fetched[0], tuple):
                continue
            messages.append((uid, email.message_from_bytes(fetched[0][1])))

        return messages


def mark_read(uid):
    username = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_APP_PASSWORD")
    if not username or not password:
        raise ValueError("Email credentials are missing in .env")

    with imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT) as mailbox:
        mailbox.login(username, password)
        mailbox.select(IMAP_MAILBOX)
        mailbox.store(uid, "+FLAGS", "\\Seen")


def message_details(message: Message):
    sender_name, sender_email = parseaddr(message.get("From", ""))
    return {
        "sender_name": _decode_header_value(sender_name) or sender_email,
        "sender_email": sender_email,
        "subject": _decode_header_value(message.get("Subject", "")),
        "body": _text_body(message),
        "message_id": message.get("Message-ID", ""),
        "references": message.get("References", ""),
    }
