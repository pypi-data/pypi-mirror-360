"""Voice command prompts for guided interactions."""

from voice_mode.server import mcp


@mcp.prompt()
async def voice_setup() -> str:
    """Guide for setting up voice services"""
    return """To set up voice services for voice-mode:

1. **Environment Variables**:
   - OPENAI_API_KEY: Your OpenAI API key (only required if using OpenAI services)
   
2. **Optional Configuration**:
   - TTS_VOICE: Default voice (e.g., 'nova', 'alloy', 'af_sky')
   - TTS_MODEL: TTS model (e.g., 'tts-1', 'tts-1-hd', 'gpt-4o-mini-tts')
   - STT_MODEL: STT model (default: 'whisper-1')
   - VOICE_MODE_PREFER_LOCAL: Use local services when available (default: true)
   - VOICE_MODE_AUTO_START_KOKORO: Auto-start Kokoro TTS (default: false)

3. **Local Services** (optional):
   - Kokoro TTS: Run `kokoro_start()` for local TTS
   - LiveKit: Set LIVEKIT_URL for room-based voice chat

4. **Quick Test**:
   ```
   # Test basic TTS
   converse("Hello! Can you hear me?", wait_for_response=False)
   
   # Test conversation
   converse("What's your name?")
   ```
"""


@mcp.prompt()
async def emotional_speech_guide() -> str:
    """Guide for using emotional speech features"""
    return """To use emotional speech with voice-mode:

**Requirements**:
- Use OpenAI API (emotional speech requires OpenAI's gpt-4o-mini-tts model)

**Usage Examples**:

```python
# Excitement
converse("We did it! This is amazing!", 
         tts_model="gpt-4o-mini-tts",
         tts_instructions="Sound extremely excited and celebratory")

# Sadness
converse("I'm sorry for your loss", 
         tts_model="gpt-4o-mini-tts",
         tts_instructions="Sound gentle and sympathetic")

# Urgency
converse("Watch out! Be careful!", 
         tts_model="gpt-4o-mini-tts",
         tts_instructions="Sound urgent and concerned")

# Humor
converse("That's the funniest thing I've heard all day!", 
         tts_model="gpt-4o-mini-tts",
         tts_instructions="Sound amused and playful")

# Whispering
converse("This is a secret", 
         tts_model="gpt-4o-mini-tts",
         tts_instructions="Whisper very quietly")
```

**Tips**:
- Be specific with emotional instructions
- Combine emotions with speaking style (e.g., "Sound excited but speak slowly")
- Cost: ~$0.02/minute for emotional speech
- Automatically uses gpt-4o-mini-tts when emotional instructions are provided
"""
