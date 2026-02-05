import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")
PUBLIC_URL = os.environ.get("PUBLIC_URL")
TARGET_NUMBER = os.environ.get("TARGET_NUMBER")


def make_call():
    """Make a single test call"""
    
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, 
                TWILIO_PHONE_NUMBER, PUBLIC_URL, TARGET_NUMBER]):
        print("ERROR: Missing environment variables!")
        print("Check your .env file")
        return
    
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    print(f"\nMaking call to {TARGET_NUMBER}")
    print(f"From: {TWILIO_PHONE_NUMBER}")
    print(f"Webhook: {PUBLIC_URL}/voice\n")
    
    try:
        call = client.calls.create(
            to=TARGET_NUMBER,
            from_=TWILIO_PHONE_NUMBER,
            url=f'{PUBLIC_URL}/voice',
            status_callback=f'{PUBLIC_URL}/status',
            status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
            method='POST'
        )
        
        print(f"✓ Call initiated!")
        print(f"Call SID: {call.sid}")
        print(f"Status: {call.status}\n")
        print("Check server logs to see conversation")
        print("Transcript will be saved when call completes\n")
        
        return call.sid
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


if __name__ == "__main__":
    make_call()
