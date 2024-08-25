import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.notifications.base_notifier import BaseNotifier

class EmailNotifier(BaseNotifier):
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.port = 587  # For starttls
        self.sender_email = os.getenv("EMAIL_SENDER")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.receiver_email = os.getenv("EMAIL_RECEIVER")

    async def notify(self, message: str) -> None:
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.receiver_email
        msg['Subject'] = "Scraper Notification"

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP(self.smtp_server, self.port)
        server.starttls()
        server.login(self.sender_email, self.password)
        text = msg.as_string()
        server.sendmail(self.sender_email, self.receiver_email, text)
        server.quit()