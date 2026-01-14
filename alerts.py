import requests, os, smtplib
from email.message import EmailMessage

def send_webhook(message):
    requests.post(os.environ["WEBHOOK_URL"], json={"text": message})

def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = os.environ["ALERT_EMAIL"]
    msg["To"] = os.environ["ALERT_EMAIL"]

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.environ["ALERT_EMAIL"], os.environ["EMAIL_PASS"])
        server.send_message(msg)
