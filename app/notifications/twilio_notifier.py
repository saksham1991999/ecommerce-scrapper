from twilio.rest import Client
from app.notifications.base_notifier import BaseNotifier
import os

class TwilioNotifier(BaseNotifier):
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_FROM_NUMBER')
        self.to_number = os.getenv('TWILIO_TO_NUMBER')
        self.client = Client(self.account_sid, self.auth_token)

    async def notify(self, message: str) -> None:
        self.client.messages.create(
            body=message,
            from_=self.from_number,
            to=self.to_number
        )