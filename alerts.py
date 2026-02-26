import smtplib
from email.mime.text import MIMEText


def send_failure_email(error_message):

    sender = "your_email@gmail.com"
    password = "your_app_password"
    receiver = "your_email@gmail.com"

    msg = MIMEText(f"Pipeline Failed:\n\n{error_message}")
    msg["Subject"] = "Stock Pipeline Failure"
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)