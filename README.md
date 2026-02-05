# Voice Bot Testing System

Automated testing tool for the Pretty Good AI voice agent (805-439-8008). Simulates realistic patient calls to find bugs and evaluate quality.

## What It Does

- Makes real phone calls to test the AI agent
- Simulates patient conversations using Claude AI  
- Records full conversation transcripts
- Automatically detects bugs and quality issues
- Generates detailed bug reports

## Setup

### Requirements

- Python 3.8+
- Twilio account with phone number
- Anthropic API key
- ngrok (for local testing)

### Installation

```bash
# Clone and install
git clone <your-repo>
cd voice-bot-testing
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials
```

### Environment Variables

Create a `.env` file with:

```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
ANTHROPIC_API_KEY=sk-ant-xxx
PUBLIC_URL=https://your-ngrok-url.ngrok-free.app
TARGET_NUMBER=+18054398008
```

### Running ngrok

```bash
# In a separate terminal
ngrok http 8000

# Copy the ngrok URL to PUBLIC_URL in .env
```

## Usage

### Start the Server

```bash
python voice_bot.py
```

### Run Tests

**Single call:**
```bash
python make_call.py
```

**Multiple calls:**
```bash
# 10 calls (default)
python run_tests.py

# Custom number
python run_tests.py 5
```

### Analyze Results

```bash
python analyze_bugs.py
```

This generates `BUG_REPORT.md` with all findings.

## Test Scenarios

The bot tests these scenarios automatically:

1. Schedule new appointment
2. Reschedule existing appointment
3. Cancel appointment
4. Prescription refill request
5. Office hours and location
6. Insurance acceptance (Medicare)
7. Urgent same-day appointment
8. COVID-19 testing
9. Medical records transfer
10. Parking and directions

## Output

### Transcripts

`transcripts/call_<SID>_<timestamp>.json`

Contains:
- Full conversation
- Timestamps
- Detected issues
- Scenario info

### Bug Report

`BUG_REPORT.md`

Organized by severity:
- Critical: System failures
- High: Major UX issues
- Medium: Noticeable problems
- Low: Polish improvements

## Architecture

**Components:**

1. **voice_bot.py** - FastAPI server handling Twilio webhooks
2. **run_tests.py** - Orchestrates multiple test calls
3. **make_call.py** - Quick single call testing
4. **analyze_bugs.py** - Processes transcripts, generates reports

**Key Design Choices:**

- **Twilio for telephony**: Reliable, built-in STT/TTS
- **Claude for responses**: Natural conversation generation
- **Sequential calls**: Each call completes before next starts
- **File-based storage**: Simple, portable transcripts

## How It Works

```
run_tests.py initiates call
    ↓
Twilio connects to 805-439-8008
    ↓
Agent answers
    ↓
voice_bot.py receives webhook
    ↓
Claude generates patient message
    ↓
Conversation loop:
  - Agent speaks
  - Twilio transcribes
  - Claude generates reply
  - Patient speaks
    ↓
Transcript saved
    ↓
analyze_bugs.py processes results
```

## Cost Estimate

Per call: **$0.50-1.00**
- Twilio: $0.40-0.80 (voice minutes + STT/TTS)
- Claude: $0.10-0.20 (API calls)

10 calls: **$5-10**

## Troubleshooting

**Calls not connecting:**
- Check ngrok is running
- Verify PUBLIC_URL in .env
- Confirm Twilio credentials

**No transcripts:**
- Ensure transcripts/ directory exists
- Check server logs for errors
- Verify calls are completing

**Missing env variables:**
- Double-check .env file exists
- Make sure all variables are set
- Restart server after changes

## Project Structure

```
.
├── voice_bot.py          # Main server
├── run_tests.py          # Test orchestrator  
├── make_call.py          # Single call helper
├── analyze_bugs.py       # Bug analyzer
├── requirements.txt      # Dependencies
├── .env.example          # Config template
├── README.md            # This file
└── transcripts/         # Call recordings
```

## Development Notes

- Server runs on port 8000
- Max 8 turns per conversation
- 10 second buffer between calls
- Auto-saves transcripts on completion

## License

MIT
