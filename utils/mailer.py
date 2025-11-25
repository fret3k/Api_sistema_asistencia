import os
import smtplib
from email.message import EmailMessage

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))


def send_email(to_email: str, subject: str, body: str):
    if not GMAIL_USER or not GMAIL_PASS:
        raise RuntimeError("GMAIL_USER/GMAIL_PASS no configurados en variables de entorno")

    msg = EmailMessage()
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(GMAIL_USER, GMAIL_PASS)
        smtp.send_message(msg)


def send_password_reset_email(to_email: str, token: str, base_url: str):
    reset_link = f"{base_url.rstrip('/')}/personal/reset/{token}"
    subject = "Recuperación de contraseña"
    body = f"Hola,\n\nSi solicitaste restablecer tu contraseña, haz clic en el siguiente enlace:\n\n{reset_link}\n\nSi no solicitaste este cambio, ignora este correo."
    send_email(to_email, subject, body)

