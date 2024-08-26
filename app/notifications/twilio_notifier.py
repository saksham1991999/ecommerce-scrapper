import logging

from twilio.rest import Client

from app.constants import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_FROM_NUMBER,
    TWILIO_TO_NUMBER,
)
from app.exceptions.notification_exceptions import NotificationException
from app.notifications.base_notifier import BaseNotifier

logger = logging.getLogger(__name__)

class TwilioNotifier(BaseNotifier):
    """
    TwilioNotifier is responsible for sending notifications via Twilio SMS.

    Attributes:
        account_sid (str): Twilio account SID.
        auth_token (str): Twilio authentication token.
        from_number (str): The phone number from which messages are sent.
        to_number (str): The phone number to which messages are sent.
        client (Client): Twilio REST client for sending messages.
    """

    def __init__(self) -> None:
        """
        Initializes the TwilioNotifier with necessary credentials and Twilio client.
        """
        self.account_sid = TWILIO_ACCOUNT_SID
        self.auth_token = TWILIO_AUTH_TOKEN
        self.from_number = TWILIO_FROM_NUMBER
        self.to_number = TWILIO_TO_NUMBER
        self.client = Client(self.account_sid, self.auth_token)

    async def notify(self, message: str) -> None:
        """
        Sends a notification message via Twilio SMS.

        Args:
            message (str): The message content to be sent.

        Raises:
            NotificationException: If the message fails to send.
        """
        try:
            logger.info("Sending message via Twilio: %s", message)
            self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.to_number
            )
            logger.info("Message sent successfully.")
        except Exception as e:
            logger.error("Failed to send message: %s", e)
            raise NotificationException(f"Failed to send message: {e}")
