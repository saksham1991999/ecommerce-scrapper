import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.constants import (
    EMAIL_PASSWORD,
    EMAIL_RECEIVER,
    EMAIL_SENDER,
    SMTP_PORT,
    SMTP_SERVER,
)
from app.exceptions.notification_exceptions import NotificationException
from app.notifications.base_notifier import BaseNotifier


class EmailNotifier(BaseNotifier):
    """
    EmailNotifier is a concrete implementation of the BaseNotifier class
    that sends notifications via email.

    Attributes:
        smtp_server (str): The SMTP server address.
        port (int): The port number for the SMTP server.
        sender_email (str): The email address from which notifications are sent.
        password (str): The password for the sender's email account.
        receiver_email (str): The email address to which notifications are sent.
    """

    def __init__(self) -> None:
        """
        Initializes the EmailNotifier with SMTP server details and email credentials.
        """
        self.smtp_server: str = SMTP_SERVER
        self.port: int = SMTP_PORT
        self.sender_email: str = EMAIL_SENDER
        self.password: str = EMAIL_PASSWORD
        self.receiver_email: str = EMAIL_RECEIVER

    async def notify(self, message: str) -> None:
        """
        Sends a notification email with the specified message.

        Args:
            message (str): The message to be sent in the notification email.

        Raises:
            NotificationException: If an error occurs while sending the email.
        """
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.receiver_email
        msg['Subject'] = "Scraper Notification"

        msg.attach(MIMEText(message, 'plain'))

        try:
            server = smtplib.SMTP(self.smtp_server, self.port)
            server.starttls()
            server.login(self.sender_email, self.password)
            text = msg.as_string()
            server.sendmail(self.sender_email, self.receiver_email, text)
        except smtplib.SMTPException as e:
            raise NotificationException(f"Failed to send email: {e}")
        finally:
            server.quit()
