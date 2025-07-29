# PyVoiceCraft

**PyVoiceCraft** is an advanced voice processing package that provides comprehensive text-to-speech (TTS) and speech recognition capabilities with 100% more functionalities than existing packages.

## Features

- 🎤 **Advanced Speech Recognition** - Multiple engine support with continuous listening
- 🔊 **Text-to-Speech** - High-quality voice synthesis with customizable profiles
- 👤 **Voice Profiles** - Personalized voice settings (male/female, pitch, speed)
- 🎵 **Audio Processing** - Pitch modification, speed control, echo effects, volume normalization
- 💬 **Voice Commands** - Command processing and execution system
- 📝 **Conversation History** - SQLite-based conversation tracking
- 🎯 **Custom Dictionary** - Add custom word pronunciations
- 📊 **Voice Memos** - Record and save audio memos
- 📈 **Usage Statistics** - Track voice usage patterns
- 🔄 **Async Support** - Non-blocking voice operations

## Installation

```bash
pip install pyvoicecraft
```

### Dependencies

PyVoiceCraft requires the following packages:
- `pyttsx3>=2.90` - Text-to-speech engine
- `SpeechRecognition>=3.8.1` - Speech recognition
- `PyAudio>=0.2.11` - Audio processing
- `numpy>=1.19.0` - Numerical operations
- `scipy>=1.5.0` - Scientific computing

## Quick Start

### Basic Text-to-Speech

```python
from pyvoicecraft import speak

# Simple text-to-speech
speak("Hello, welcome to PyVoiceCraft!")

# With different voice
speak("This is a male voice", voice="male")
speak("This is a female voice", voice="female")
```

### Voice Recognition

```python
from pyvoicecraft import listen

# Listen for voice input
text = listen(timeout=5)
print(f"You said: {text}")
```

### Advanced Usage

```python
from pyvoicecraft import PyVoiceCraft

# Create instance
ps = PyVoiceCraft()

# Set voice profile
ps.set_profile("female")

# Speak with custom settings
ps.speak("Hello world!", save_to_file="greeting.wav")

# Start conversation
def handle_response(text):
    return f"You said: {text}"

ps.start_conversation(callback=handle_response)
```

### Voice Profiles

```python
from pyvoicecraft import PyVoiceCraft, VoiceProfile

ps = PyVoiceCraft()

# Create custom profile
custom_profile = VoiceProfile(
    name="assistant",
    gender="female",
    age=25,
    accent="neutral",
    pitch=1.1,
    speed=1.2
)

ps.add_profile(custom_profile)
ps.set_profile("assistant")
ps.speak("Hello with custom voice profile!")
```

### Voice Commands

```python
from pyvoicecraft import PyVoiceCraft

ps = PyVoiceCraft()

# Add voice commands
def time_command(text):
    ps.speak_time()

def date_command(text):
    ps.speak_date()

ps.commands.add_command("time", time_command, ["what time", "current time"])
ps.commands.add_command("date", date_command, ["what date", "today"])

# Start listening for commands
ps.commands.start_listening()
```

### Audio Effects

```python
from pyvoicecraft import PyVoiceCraft

ps = PyVoiceCraft()

# Apply audio effects
effects = {
    "echo": {"delay_ms": 500, "decay": 0.3},
    "pitch": {"factor": 1.2},
    "speed": {"factor": 0.9}
}

ps.speak("This text has audio effects", effects=effects)
```

## API Reference

### Main Classes

- **PyVoiceCraft** - Main class with all functionalities
- **VoiceProfile** - Voice profile management
- **VoiceRecognizer** - Speech recognition handling
- **VoiceCommands** - Command processing
- **AudioProcessor** - Audio effects and processing

### Quick Functions

- `speak(text, voice="female", **kwargs)` - Quick text-to-speech
- `listen(timeout=5, language="en-US")` - Quick voice recognition
- `create_male_voice()` - Create male voice instance
- `create_female_voice()` - Create female voice instance
- `get_available_voices()` - List system voices

## Examples

### Voice Memo Recording

```python
from pyvoicecraft import PyVoiceCraft

ps = PyVoiceCraft()
memo_path = ps.create_voice_memo(duration=10)
print(f"Voice memo saved to: {memo_path}")
```

### Custom Word Pronunciation

```python
from pyvoicecraft import PyVoiceCraft

ps = PyVoiceCraft()

# Add custom pronunciations
ps.add_word("API", "A P I")
ps.add_word("JSON", "Jay-son")

ps.speak("The API returns JSON data")
```

### Export/Import Data

```python
from pyvoicecraft import PyVoiceCraft

ps = PyVoiceCraft()

# Export all data
ps.export_data("backup.json")

# Import data
ps.import_data("backup.json")
```

## System Requirements

- Python 3.7+
- Windows, macOS, or Linux
- Microphone (for speech recognition)
- Speakers/headphones (for audio output)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

If you encounter any issues or have questions:
- Create an issue on [GitHub Issues](https://github.com/kodukulla-phani-kumar/pyvoicecraft/issues)
- Email: phanikumark715@gmail.com

## Changelog

### v1.0.0
- Initial release
- Text-to-speech functionality
- Speech recognition
- Voice profiles
- Audio processing effects
- Voice commands
- Conversation history
- Custom dictionary support

## Author

**Kodukulla.Phani Kumar**
- Email: phanikumark715@gmail.com
- GitHub: [@kodukulla-phani-kumar](https://github.com/kodukulla-phani-kumar)

---

⭐ If you find PyVoiceCraft useful, please give it a star on GitHub!