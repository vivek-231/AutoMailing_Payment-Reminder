import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv


load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")


def send_email(
    to_email,
    subject,
    body,
    in_reply_to=None,
    references=None,
    timeout=40
):

    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        raise ValueError("Email credentials are missing in .env")

    msg = EmailMessage()

    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject

    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
    if references:
        msg["References"] = references

    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=timeout) as server:

        server.login(
            EMAIL_ADDRESS,
            EMAIL_APP_PASSWORD
        )

        server.send_message(msg)

    print("\n✅ EMAIL SENT")
    print("To      :", to_email)
    print("Subject :", subject)