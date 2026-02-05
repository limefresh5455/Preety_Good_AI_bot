# Architecture

## System Design

This voice bot tests the Pretty Good AI agent through automated phone conversations. The system prioritizes simplicity and reliability while providing comprehensive bug detection.

**Core Components:**

1. **Voice Bot Server (voice_bot.py)** - FastAPI application handling Twilio webhooks, managing conversation state, and coordinating with Claude for response generation

2. **Call Orchestrator (run_tests.py)** - Runs multiple test calls sequentially, polling Twilio's API to wait for each call to complete before starting the next

3. **Bug Analyzer (analyze_bugs.py)** - Post-processes transcripts using heuristics and pattern matching to identify issues across all calls

## Key Design Decisions

**Why Twilio for telephony?**  
Reliable voice infrastructure with built-in speech recognition and text-to-speech. Webhook-based architecture integrates cleanly with FastAPI. No need for separate STT/TTS services.

**Why Claude for patient simulation?**  
Generates contextually appropriate responses that maintain conversation coherence. Can adapt to unexpected agent replies. More realistic than scripted responses and simpler than training a custom model.

**Why sequential call processing?**  
Prevents race conditions and makes debugging easier. The Pretty Good AI agent likely processes calls sequentially anyway. Reduces API rate limit concerns and cost exposure. Sequential execution with polling ensures each call fully completes before starting the next.

**Why file-based transcript storage?**  
Calls are short-lived (2-5 minutes). No need for database complexity. Files are portable and version-controllable. Easy to inspect and debug.

**Why two-phase bug detection?**  
Real-time heuristics catch obvious issues during the call. Post-processing analysis identifies patterns across multiple calls. This combination provides both immediate feedback and aggregate insights.

## Data Flow

```
User runs run_tests.py
    ↓
Script makes call via Twilio API
    ↓
Twilio connects to agent (805-439-8008)
    ↓
Agent answers, Twilio hits /voice webhook
    ↓
ConversationManager initializes with scenario
    ↓
Claude generates first patient message
    ↓
Twilio plays message to agent
    ↓
Agent responds → Twilio transcribes → /handle-speech
    ↓
System analyzes response, Claude generates reply
    ↓
Loop continues until max turns or goodbye
    ↓
Transcript saved as JSON
    ↓
run_tests.py polls until call completes
    ↓
Next call starts
    ↓
After all calls: analyze_bugs.py generates report
```

## Latency Optimization

**Prompt Engineering:** Shortened Claude prompts to 50-100 tokens (was 200+) for faster generation while maintaining quality

**Token Limits:** Reduced max_tokens from 150 to 100 for patient responses - sufficient for natural 1-2 sentence replies

**Early Termination:** Checks for conversation end conditions immediately rather than always generating next response

**No External Dependencies:** Using only Twilio's built-in STT/TTS eliminates additional API round-trips

Result: 2-3 second response time per turn (acceptable for phone conversations)

## Technology Stack

- **FastAPI**: Modern async framework, excellent webhook handling
- **Twilio**: Industry-standard telephony, reliable STT/TTS
- **Claude (Anthropic)**: Best conversational AI for context understanding
- **Python 3.8+**: Clean, readable, great library ecosystem

## Scalability Notes

Current system handles 10-20 sequential calls reliably. For production scale:
- Add PostgreSQL for transcript storage
- Implement connection pooling and rate limiting  
- Deploy to cloud infrastructure (AWS/GCP)
- Add monitoring and alerting
- Support parallel call handling with queue management

## Security

- API keys in environment variables (never committed)
- Webhook signature verification recommended for production
- No PII exposure in test environment
- Local transcript storage only

## Error Handling

- Try-except blocks around all external API calls
- Graceful fallbacks (end conversation on errors)
- Status webhooks track call completion
- Transcripts saved even if server crashes mid-call
