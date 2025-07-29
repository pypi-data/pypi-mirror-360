"""
PyVoiceCraft - Advanced Voice Processing Package
Author: Kodukulla.Phani Kumar
Email: phanikumark715@gmail.com
Version: 1.0.0

A comprehensive voice package with advanced functionalities for text-to-speech,
voice recognition, voice effects, and audio processing.
"""

from .pyvoicecraft import (
    PyVoiceCraft,
    VoiceProfile,
    VoiceRecognizer,
    VoiceCommands,
    AudioProcessor,
    PyVoiceCraftError,
    speak,
    listen,
    create_male_voice,
    create_female_voice,
    get_available_voices,
    quick_conversation
)

__version__ = "1.0.0"
__author__ = "Kodukulla.Phani Kumar"
__email__ = "phanikumark715@gmail.com"
__description__ = "Advanced voice processing package with comprehensive TTS and speech recognition capabilities"
__url__ = "https://github.com/kodukulla-phani-kumar/pyvoicecraft"

__all__ = [
    'PyVoiceCraft',
    'VoiceProfile',
    'VoiceRecognizer',
    'VoiceCommands',
    'AudioProcessor',
    'PyVoiceCraftError',
    'speak',
    'listen',
    'create_male_voice',
    'create_female_voice',
    'get_available_voices',
    'quick_conversation'
]