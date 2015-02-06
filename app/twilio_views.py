from app import views, app, client
from config import TWILIO_NUMBER
import twilio

@app.route('/twilio/send_message')
@login_required
def send_message():
    user = g.user
    try:
        message = client.messages.create(
                body="Radhika I love you <3",
                to="+17608213933",
                from_=TWILIO_NUMBER
    )
    except twilio.TwilioRestException as e:
        print e
