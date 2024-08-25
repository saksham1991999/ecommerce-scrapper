from twilio.rest import Client
from app.notifications.base_notifier import BaseNotifier
from app.constants import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, TWILIO_TO_NUMBER

class TwilioNotifier(BaseNotifier):
    def __init__(self):
        self.account_sid = TWILIO_ACCOUNT_SID
        self.auth_token = TWILIO_AUTH_TOKEN
        self.from_number = TWILIO_FROM_NUMBER
        self.to_number = TWILIO_TO_NUMBER
        self.client = Client(self.account_sid, self.auth_token)

    async def notify(self, message: str) -> None:
        self.client.messages.create(
            body=message,
            from_=self.from_number,
            to=self.to_number
        )