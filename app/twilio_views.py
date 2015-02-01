from app import views, app, client
from config import TWILIO_NUMBER
import twilio

try:
    message = client.messages.create(
                body="Radhika I love you <3",
                to="+17608213933",
                from_=TWILIO_NUMBER
    )
except twilio.TwilioRestException as e:
    print e
print message.sid

