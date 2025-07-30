import smtplib
from email.message import EmailMessage
import re

def is_valid_email(email):
    regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(regex, email) is not None

def send_email(to, subject, body, sender, password, smtp_server="smtp.gmail.com", port=587):
    if not is_valid_email(sender):
        raise ValueError(f"Invalid sender email address: {sender}")
    if not is_valid_email(to):
        raise ValueError(f"Invalid recipient email address: {to}")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg.set_content(body)

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
