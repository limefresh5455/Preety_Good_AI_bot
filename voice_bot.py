"""
Voice Bot for Testing Pretty Good AI Agent
Simulates patient calling medical office - finds bugs and tests quality
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List
from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
import anthropic
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Config
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "https://your-ngrok-url.ngrok-free.app")
TARGET_NUMBER = os.environ.get("TARGET_NUMBER")

# Store active conversations
conversations: Dict[str, Dict] = {}
transcripts_dir = "transcripts"
os.makedirs(transcripts_dir, exist_ok=True)


class ConversationManager:
    """Tracks conversation state for each call"""
    
    def __init__(self, call_sid: str, scenario: str):
        self.call_sid = call_sid
        self.scenario = scenario
        self.messages: List[Dict] = []
        self.turn_count = 0
        self.start_time = datetime.now()
        self.issues = []
        
    def add_message(self, speaker: str, text: str):
        self.messages.append({
            "speaker": speaker,
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
        
    def generate_patient_response(self) -> str:
        """Use Claude to generate next patient message"""
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        # Build context from conversation
        history = "\n".join([
            f"{msg['speaker']}: {msg['text']}" for msg in self.messages
        ])
        
        # Shorter, faster prompt for lower latency
        prompt = f"""You are a patient calling about: {self.scenario}

Conversation:
{history}

Reply naturally as the patient (1-2 sentences). If done, say "Thanks, goodbye."

Response:"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,  # Reduced for speed
            messages=[{"role": "user", "content": prompt}]
        )
        
        response = message.content[0].text.strip()
        self.turn_count += 1
        return response
    
    def check_for_issues(self, agent_text: str):
        """Quick heuristic checks for common problems"""
        
        if len(agent_text) > 400:
            self.issues.append("Response too verbose")
            
        uncertainty_words = ["i don't know", "not sure", "i can't", "unable to"]
        if any(phrase in agent_text.lower() for phrase in uncertainty_words):
            self.issues.append("Agent expressed uncertainty")
            
        # Check for hallucinations in first response
        if self.turn_count == 1:
            specific_details = ["2pm", "3pm", "monday", "tuesday", "dr.", "doctor"]
            if any(detail in agent_text.lower() for detail in specific_details):
                self.issues.append("May be hallucinating specific details")
        
    def should_end_conversation(self, text: str) -> bool:
        """Check if conversation should end"""
        goodbye_phrases = ["goodbye", "bye", "thank you for calling"]
        return (self.turn_count >= 8 or 
                any(phrase in text.lower() for phrase in goodbye_phrases))
        
    def save_transcript(self):
        filename = f"{transcripts_dir}/call_{self.call_sid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            "call_sid": self.call_sid,
            "scenario": self.scenario,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration": (datetime.now() - self.start_time).total_seconds(),
            "turns": self.turn_count,
            "messages": self.messages,
            "issues": self.issues
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved transcript: {filename}")


# Test scenarios
SCENARIOS = [
    # Orthopedics-specific scenarios (priority)
    "Schedule an appointment for knee pain that started after running",
    "Request a follow-up appointment after recent knee surgery",
    "Ask about treatment options for shoulder pain",
    "Schedule an appointment for back pain that's been ongoing for weeks",
    "Request an MRI or X-ray appointment for hip pain",
    "Ask if they treat sports injuries and torn ACL",
    "Reschedule a post-surgery follow-up appointment",
    "Ask about physical therapy referrals for ankle sprain",
    "Schedule a consultation for arthritis in hands",
    "Ask about office hours and if they accept workers' compensation",
    # General medical office scenarios
    "Cancel an upcoming appointment",
    "Ask about office location and parking",
    "Request medical records from previous visit",
    "Ask if they accept Medicare or specific insurance",
    "Schedule an urgent same-day appointment for injury"
]

@app.post("/voice")
async def initial_call(request: Request):
    """Handle initial call connection"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    
    # Pick scenario based on call
    scenario_idx = hash(call_sid) % len(SCENARIOS)
    scenario = SCENARIOS[scenario_idx]
    
    # Initialize conversation
    conv = ConversationManager(call_sid, scenario)
    conversations[call_sid] = conv
    
    # Generate first patient message
    first_msg = conv.generate_patient_response()
    conv.add_message("Patient", first_msg)
    
    print(f"\nCall started: {call_sid}")
    print(f"Scenario: {scenario}")
    print(f"Patient: {first_msg}")
    
    # Build response with Twilio TTS
    response = VoiceResponse()
    gather = Gather(
        input='speech',
        action=f'{PUBLIC_URL}/handle-speech',
        method='POST',
        speech_timeout='auto',
        language='en-US'
    )
    
    # Use Twilio's neural voice for better quality
    gather.say(first_msg, voice='Polly.Joanna')
    response.append(gather)
    
    # If no response, retry once
    response.say("I didn't hear you. Let me repeat that.", voice='Polly.Joanna')
    response.redirect(f'{PUBLIC_URL}/handle-speech')
    
    return Response(content=str(response), media_type="application/xml")


@app.post("/handle-speech")
async def handle_speech(request: Request):
    """Process agent's speech and continue conversation"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    agent_speech = form_data.get("SpeechResult", "")
    
    print(f"Agent: {agent_speech}")
    
    conv = conversations.get(call_sid)
    if not conv:
        # Call ended or not found
        response = VoiceResponse()
        response.hangup()
        return Response(content=str(response), media_type="application/xml")
    
    # Record agent response
    conv.add_message("Agent", agent_speech)
    conv.check_for_issues(agent_speech)
    
    # Check if we should end
    if conv.should_end_conversation(agent_speech) or not agent_speech:
        conv.save_transcript()
        response = VoiceResponse()
        response.say("Thank you, goodbye.", voice='Polly.Joanna')
        response.hangup()
        return Response(content=str(response), media_type="application/xml")
    
    # Generate next patient response
    next_msg = conv.generate_patient_response()
    conv.add_message("Patient", next_msg)
    print(f"Patient: {next_msg}")
    
    # Check if patient is ending call
    if conv.should_end_conversation(next_msg):
        conv.save_transcript()
        response = VoiceResponse()
        response.say(next_msg, voice='Polly.Joanna')
        response.hangup()
        return Response(content=str(response), media_type="application/xml")
    
    # Continue conversation
    response = VoiceResponse()
    gather = Gather(
        input='speech',
        action=f'{PUBLIC_URL}/handle-speech',
        method='POST',
        speech_timeout='auto',
        language='en-US'
    )
    
    gather.say(next_msg, voice='Polly.Joanna')
    response.append(gather)
    
    # Fallback
    response.say("Sorry, I didn't catch that. Goodbye.", voice='Polly.Joanna')
    response.hangup()
    
    return Response(content=str(response), media_type="application/xml")


@app.post("/status")
async def call_status(request: Request):
    """Track call completion"""
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    status = form_data.get("CallStatus")
    
    print(f"Call {call_sid}: {status}")
    
    # Clean up when call ends
    if status in ["completed", "failed", "busy", "no-answer"]:
        if call_sid in conversations:
            conv = conversations[call_sid]
            if conv.messages:
                conv.save_transcript()
            del conversations[call_sid]
    
    return Response(content="OK")


@app.get("/")
async def health():
    return {
        "status": "running",
        "active_calls": len(conversations)
    }


def make_call():
    """Initiate a call to the test number"""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    print(f"\nCalling {TARGET_NUMBER}")
    
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
        return call.sid
        
    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
