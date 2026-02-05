import os
import sys
import time
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")
PUBLIC_URL = os.environ.get("PUBLIC_URL")
TARGET_NUMBER = os.environ.get("TARGET_NUMBER")


def wait_for_call_completion(client, call_sid, timeout=300):
    """
    Poll Twilio API until call completes
    Returns True if completed successfully, False if timeout
    """
    start = time.time()
    print(f"Waiting for call {call_sid} to complete...")
    
    while time.time() - start < timeout:
        call = client.calls(call_sid).fetch()
        status = call.status
        
        if status in ["completed", "failed", "busy", "no-answer", "canceled"]:
            print(f"Call ended with status: {status}")
            return status == "completed"

        time.sleep(5)
    
    print("Call timeout - moving on")
    return False


def make_test_call(client, call_number, total_calls):
    """Make a single test call and wait for it to complete"""
    
    print(f"\n{'='*60}")
    print(f"Call {call_number}/{total_calls}")
    print(f"{'='*60}")
    
    try:
        call = client.calls.create(
            to=TARGET_NUMBER,
            from_=TWILIO_PHONE_NUMBER,
            url=f'{PUBLIC_URL}/voice',
            status_callback=f'{PUBLIC_URL}/status',
            status_callback_event=['completed'],
            method='POST'
        )
        
        print(f"Call initiated: {call.sid}")
        
        success = wait_for_call_completion(client, call.sid)
        
        if success:
            print(f"✓ Call {call_number} completed successfully")
        else:
            print(f"✗ Call {call_number} ended unexpectedly")
        
        return call.sid, success
        
    except Exception as e:
        print(f"✗ Error making call: {e}")
        return None, False


def run_tests(num_calls=10):
    """Run test suite - waits for each call to finish"""
    
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, 
                TWILIO_PHONE_NUMBER, PUBLIC_URL, TARGET_NUMBER]):
        print("ERROR: Missing environment variables!")
        print("Check your .env file")
        return
    
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    print(f"\n{'='*60}")
    print(f"Starting test suite: {num_calls} calls")
    print(f"Target: {TARGET_NUMBER}")
    print(f"{'='*60}\n")
    
    results = []
    successful = 0
    
    for i in range(num_calls):
        call_sid, success = make_test_call(client, i+1, num_calls)
        
        if call_sid:
            results.append(call_sid)
            if success:
                successful += 1
        
        if i < num_calls - 1:
            print("\nWaiting 10 seconds before next call...\n")
            time.sleep(10)
    
    print(f"\n{'='*60}")
    print(f"Test suite complete")
    print(f"Successful calls: {successful}/{num_calls}")
    print(f"{'='*60}\n")
    
    return results


if __name__ == "__main__":
    num_calls = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    run_tests(num_calls)
