"""
Pyvoice - Advanced Voice Processing Package
Author: Kodukulla.Phani Kumar
Email: phanikumark715@gmail.com
Version: 1.0.0

A comprehensive voice package with 100% more functionalities than existing packages.
Includes text-to-speech, voice recognition, voice effects, and audio processing.
"""

import os
import sys
import time
import threading
import queue
import json
import tempfile
import wave
import audioop
import math
import random
from typing import List, Dict, Optional, Tuple, Union, Callable
from pathlib import Path
import sqlite3
from datetime import datetime

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyaudio
except ImportError:
    pyaudio = None

try:
    import numpy as np
except ImportError:
    np = None

try:
    import scipy.io.wavfile as wav
    from scipy import signal
except ImportError:
    wav = None
    signal = None


class PyvoiceError(Exception):
    """Custom exception for Pyvoice package."""
    pass


class VoiceProfile:
    """Voice profile management for personalized voice settings."""
    
    def __init__(self, name: str, gender: str = "neutral", age: int = 30, 
                 accent: str = "neutral", pitch: float = 1.0, speed: float = 1.0):
        self.name = name
        self.gender = gender.lower()
        self.age = age
        self.accent = accent.lower()
        self.pitch = pitch
        self.speed = speed
        self.created_at = datetime.now()
        self.usage_count = 0
        
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'accent': self.accent,
            'pitch': self.pitch,
            'speed': self.speed,
            'created_at': self.created_at.isoformat(),
            'usage_count': self.usage_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        profile = cls(
            name=data['name'],
            gender=data['gender'],
            age=data['age'],
            accent=data['accent'],
            pitch=data['pitch'],
            speed=data['speed']
        )
        profile.created_at = datetime.fromisoformat(data['created_at'])
        profile.usage_count = data['usage_count']
        return profile


class AudioProcessor:
    """Advanced audio processing utilities."""
    
    @staticmethod
    def change_pitch(audio_data: bytes, sample_rate: int, pitch_factor: float) -> bytes:
        """Change pitch of audio data."""
        if not np:
            raise PyvoiceError("NumPy required for pitch modification")
        
        # Convert bytes to numpy array
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        
        # Simple pitch shifting using resampling
        indices = np.round(np.arange(0, len(audio_np), pitch_factor))
        indices = indices[indices < len(audio_np)].astype(int)
        pitched_audio = audio_np[indices]
        
        return pitched_audio.astype(np.int16).tobytes()
    
    @staticmethod
    def change_speed(audio_data: bytes, speed_factor: float) -> bytes:
        """Change speed of audio data."""
        if not np:
            raise PyvoiceError("NumPy required for speed modification")
        
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        
        # Resample for speed change
        indices = np.round(np.arange(0, len(audio_np), speed_factor))
        indices = indices[indices < len(audio_np)].astype(int)
        speed_audio = audio_np[indices]
        
        return speed_audio.astype(np.int16).tobytes()
    
    @staticmethod
    def add_echo(audio_data: bytes, delay_ms: int = 500, decay: float = 0.3) -> bytes:
        """Add echo effect to audio."""
        if not np:
            raise PyvoiceError("NumPy required for echo effect")
        
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        delay_samples = int(delay_ms * 44100 / 1000)  # Assuming 44.1kHz
        
        # Create echo
        echo_audio = np.zeros(len(audio_np) + delay_samples, dtype=np.float32)
        echo_audio[:len(audio_np)] += audio_np.astype(np.float32)
        echo_audio[delay_samples:delay_samples + len(audio_np)] += audio_np.astype(np.float32) * decay
        
        # Normalize and convert back
        echo_audio = np.clip(echo_audio, -32768, 32767)
        return echo_audio.astype(np.int16).tobytes()
    
    @staticmethod
    def normalize_volume(audio_data: bytes, target_level: float = 0.8) -> bytes:
        """Normalize audio volume."""
        if not np:
            raise PyvoiceError("NumPy required for volume normalization")
        
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        
        # Calculate current max amplitude
        max_amplitude = np.max(np.abs(audio_np))
        if max_amplitude == 0:
            return audio_data
        
        # Normalize
        normalized = audio_np * (target_level * 32767 / max_amplitude)
        normalized = np.clip(normalized, -32768, 32767)
        
        return normalized.astype(np.int16).tobytes()


class VoiceRecognizer:
    """Advanced voice recognition with multiple engines."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer() if sr else None
        self.microphone = sr.Microphone() if sr else None
        self.is_listening = False
        self.recognition_thread = None
        self.callback_queue = queue.Queue()
        
    def listen_once(self, timeout: int = 5, language: str = "en-US") -> str:
        """Listen for a single voice command."""
        if not self.recognizer:
            raise PyvoiceError("SpeechRecognition package required")
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout)
            text = self.recognizer.recognize_google(audio, language=language)
            return text
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            raise PyvoiceError(f"Recognition error: {e}")
    
    def listen_continuous(self, callback: Callable[[str], None], language: str = "en-US"):
        """Start continuous voice recognition."""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.recognition_thread = threading.Thread(
            target=self._continuous_recognition,
            args=(callback, language)
        )
        self.recognition_thread.daemon = True
        self.recognition_thread.start()
    
    def stop_listening(self):
        """Stop continuous voice recognition."""
        self.is_listening = False
        if self.recognition_thread:
            self.recognition_thread.join()
    
    def _continuous_recognition(self, callback: Callable[[str], None], language: str):
        """Internal continuous recognition loop."""
        while self.is_listening:
            try:
                text = self.listen_once(timeout=1, language=language)
                if text:
                    callback(text)
            except:
                continue
            time.sleep(0.1)


class VoiceCommands:
    """Voice command processing and execution."""
    
    def __init__(self):
        self.commands = {}
        self.recognizer = VoiceRecognizer()
        
    def add_command(self, command: str, callback: Callable[[str], None], 
                   aliases: List[str] = None):
        """Add a voice command."""
        self.commands[command.lower()] = callback
        if aliases:
            for alias in aliases:
                self.commands[alias.lower()] = callback
    
    def remove_command(self, command: str):
        """Remove a voice command."""
        if command.lower() in self.commands:
            del self.commands[command.lower()]
    
    def process_command(self, text: str) -> bool:
        """Process a voice command."""
        text = text.lower().strip()
        
        for command, callback in self.commands.items():
            if command in text:
                try:
                    callback(text)
                    return True
                except Exception as e:
                    print(f"Error executing command '{command}': {e}")
                    return False
        return False
    
    def start_listening(self, language: str = "en-US"):
        """Start listening for voice commands."""
        def command_callback(text: str):
            self.process_command(text)
        
        self.recognizer.listen_continuous(command_callback, language)
    
    def stop_listening(self):
        """Stop listening for voice commands."""
        self.recognizer.stop_listening()


class Pyvoice:
    """Main Pyvoice class with comprehensive voice functionalities."""
    
    def __init__(self, data_dir: str = None):
        self.engine = None
        self.voice_profiles = {}
        self.current_profile = None
        self.audio_processor = AudioProcessor()
        self.recognizer = VoiceRecognizer()
        self.commands = VoiceCommands()
        self.conversation_history = []
        self.custom_dictionary = {}
        
        # Initialize data directory
        self.data_dir = Path(data_dir) if data_dir else Path.home() / ".pyvoice"
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self.db_path = self.data_dir / "pyvoice.db"
        self._init_database()
        
        # Initialize TTS engine
        self._init_tts_engine()
        
        # Load profiles
        self._load_profiles()
        
        # Create default profiles
        self._create_default_profiles()
    
    def _init_database(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                type TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                pronunciation TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _init_tts_engine(self):
        """Initialize text-to-speech engine."""
        if pyttsx3:
            self.engine = pyttsx3.init()
            # Set default properties
            self.engine.setProperty('rate', 200)
            self.engine.setProperty('volume', 1.0)
    
    def _load_profiles(self):
        """Load voice profiles from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, data FROM voice_profiles')
        rows = cursor.fetchall()
        
        for name, data in rows:
            profile_data = json.loads(data)
            self.voice_profiles[name] = VoiceProfile.from_dict(profile_data)
        
        conn.close()
    
    def _create_default_profiles(self):
        """Create default male and female voice profiles."""
        if "male" not in self.voice_profiles:
            male_profile = VoiceProfile("male", "male", 35, "neutral", 0.8, 1.0)
            self.add_profile(male_profile)
        
        if "female" not in self.voice_profiles:
            female_profile = VoiceProfile("female", "female", 28, "neutral", 1.2, 1.1)
            self.add_profile(female_profile)
        
        # Set default profile
        if not self.current_profile:
            self.current_profile = self.voice_profiles.get("female")
    
    def add_profile(self, profile: VoiceProfile):
        """Add a voice profile."""
        self.voice_profiles[profile.name] = profile
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO voice_profiles (name, data)
            VALUES (?, ?)
        ''', (profile.name, json.dumps(profile.to_dict())))
        
        conn.commit()
        conn.close()
    
    def get_profile(self, name: str) -> Optional[VoiceProfile]:
        """Get a voice profile by name."""
        return self.voice_profiles.get(name)
    
    def set_profile(self, name: str):
        """Set current voice profile."""
        if name in self.voice_profiles:
            self.current_profile = self.voice_profiles[name]
            self.current_profile.usage_count += 1
            self.add_profile(self.current_profile)  # Update database
        else:
            raise PyvoiceError(f"Profile '{name}' not found")
    
    def list_profiles(self) -> List[str]:
        """List all available voice profiles."""
        return list(self.voice_profiles.keys())
    
    def speak(self, text: str, profile: str = None, save_to_file: str = None, 
             effects: Dict = None) -> bool:
        """Speak text with advanced options."""
        if not self.engine:
            raise PyvoiceError("TTS engine not available")
        
        # Use specified profile or current profile
        if profile:
            original_profile = self.current_profile
            self.set_profile(profile)
        
        try:
            # Apply current profile settings
            if self.current_profile:
                rate = int(200 * self.current_profile.speed)
                self.engine.setProperty('rate', rate)
                
                # Set voice gender if available
                voices = self.engine.getProperty('voices')
                if voices:
                    if self.current_profile.gender == "female":
                        female_voices = [v for v in voices if "female" in v.name.lower() or "woman" in v.name.lower()]
                        if female_voices:
                            self.engine.setProperty('voice', female_voices[0].id)
                    elif self.current_profile.gender == "male":
                        male_voices = [v for v in voices if "male" in v.name.lower() or "man" in v.name.lower()]
                        if male_voices:
                            self.engine.setProperty('voice', male_voices[0].id)
            
            # Process custom dictionary
            processed_text = self._process_custom_words(text)
            
            # Save to conversation history
            self._save_to_history(processed_text, "speech")
            
            if save_to_file:
                self.engine.save_to_file(processed_text, save_to_file)
                self.engine.runAndWait()
            else:
                self.engine.say(processed_text)
                self.engine.runAndWait()
            
            return True
            
        except Exception as e:
            raise PyvoiceError(f"Speech error: {e}")
        finally:
            # Restore original profile if changed
            if profile and 'original_profile' in locals():
                self.current_profile = original_profile
    
    def speak_async(self, text: str, callback: Callable = None, **kwargs):
        """Speak text asynchronously."""
        def speak_thread():
            try:
                self.speak(text, **kwargs)
                if callback:
                    callback(True)
            except Exception as e:
                if callback:
                    callback(False)
        
        thread = threading.Thread(target=speak_thread)
        thread.daemon = True
        thread.start()
        return thread
    
    def listen(self, timeout: int = 5, language: str = "en-US") -> str:
        """Listen for voice input."""
        text = self.recognizer.listen_once(timeout, language)
        if text:
            self._save_to_history(text, "recognition")
        return text
    
    def start_conversation(self, callback: Callable[[str], str] = None, 
                          language: str = "en-US"):
        """Start a voice conversation."""
        def conversation_callback(text: str):
            self._save_to_history(text, "recognition")
            if callback:
                response = callback(text)
                if response:
                    self.speak(response)
        
        self.recognizer.listen_continuous(conversation_callback, language)
    
    def stop_conversation(self):
        """Stop voice conversation."""
        self.recognizer.stop_listening()
    
    def add_word(self, word: str, pronunciation: str):
        """Add custom word pronunciation."""
        self.custom_dictionary[word.lower()] = pronunciation
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO custom_words (word, pronunciation)
            VALUES (?, ?)
        ''', (word.lower(), pronunciation))
        
        conn.commit()
        conn.close()
    
    def get_word_pronunciation(self, word: str) -> Optional[str]:
        """Get custom pronunciation for a word."""
        return self.custom_dictionary.get(word.lower())
    
    def _process_custom_words(self, text: str) -> str:
        """Process text with custom word pronunciations."""
        words = text.split()
        processed_words = []
        
        for word in words:
            clean_word = word.lower().strip('.,!?;:')
            if clean_word in self.custom_dictionary:
                processed_words.append(self.custom_dictionary[clean_word])
            else:
                processed_words.append(word)
        
        return ' '.join(processed_words)
    
    def _save_to_history(self, text: str, type_: str):
        """Save text to conversation history."""
        self.conversation_history.append({
            'text': text,
            'type': type_,
            'timestamp': datetime.now()
        })
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversation_history (text, type)
            VALUES (?, ?)
        ''', (text, type_))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, limit: int = 100) -> List[Dict]:
        """Get conversation history."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT text, type, timestamp FROM conversation_history
            ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{'text': row[0], 'type': row[1], 'timestamp': row[2]} for row in rows]
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM conversation_history')
        conn.commit()
        conn.close()
    
    def get_available_voices(self) -> List[Dict]:
        """Get available TTS voices."""
        if not self.engine:
            return []
        
        voices = self.engine.getProperty('voices')
        if not voices:
            return []
        
        voice_list = []
        for voice in voices:
            voice_info = {
                'id': voice.id,
                'name': voice.name,
                'languages': getattr(voice, 'languages', []),
                'gender': getattr(voice, 'gender', 'unknown'),
                'age': getattr(voice, 'age', 'unknown')
            }
            voice_list.append(voice_info)
        
        return voice_list
    
    def set_voice_by_id(self, voice_id: str):
        """Set TTS voice by ID."""
        if self.engine:
            self.engine.setProperty('voice', voice_id)
    
    def get_voice_info(self) -> Dict:
        """Get current voice information."""
        if not self.engine:
            return {}
        
        current_voice = self.engine.getProperty('voice')
        voices = self.engine.getProperty('voices')
        
        if voices:
            for voice in voices:
                if voice.id == current_voice:
                    return {
                        'id': voice.id,
                        'name': voice.name,
                        'languages': getattr(voice, 'languages', []),
                        'gender': getattr(voice, 'gender', 'unknown'),
                        'age': getattr(voice, 'age', 'unknown')
                    }
        
        return {}
    
    def set_speech_rate(self, rate: int):
        """Set speech rate (words per minute)."""
        if self.engine:
            self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """Set speech volume (0.0 to 1.0)."""
        if self.engine:
            volume = max(0.0, min(1.0, volume))
            self.engine.setProperty('volume', volume)
    
    def pause_speech(self):
        """Pause current speech."""
        if self.engine:
            self.engine.stop()
    
    def resume_speech(self):
        """Resume paused speech."""
        if self.engine:
            self.engine.runAndWait()
    
    def is_speaking(self) -> bool:
        """Check if currently speaking."""
        if self.engine:
            return self.engine.isBusy()
        return False
    
    def wait_until_done(self):
        """Wait until speech is complete."""
        if self.engine:
            self.engine.runAndWait()
    
    def spell_word(self, word: str):
        """Spell out a word letter by letter."""
        spelled = ' '.join(word.upper())
        self.speak(spelled)
    
    def speak_number(self, number: Union[int, float], as_digits: bool = False):
        """Speak a number with options."""
        if as_digits:
            digits = ' '.join(str(number))
            self.speak(digits)
        else:
            self.speak(str(number))
    
    def speak_time(self, format_12h: bool = True):
        """Speak current time."""
        now = datetime.now()
        if format_12h:
            time_str = now.strftime("%I:%M %p")
        else:
            time_str = now.strftime("%H:%M")
        
        self.speak(f"The current time is {time_str}")
    
    def speak_date(self, format_long: bool = True):
        """Speak current date."""
        now = datetime.now()
        if format_long:
            date_str = now.strftime("%B %d, %Y")
        else:
            date_str = now.strftime("%m/%d/%Y")
        
        self.speak(f"Today is {date_str}")
    
    def create_voice_memo(self, filename: str = None, duration: int = 10) -> str:
        """Create a voice memo."""
        if not filename:
            filename = f"memo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        
        filepath = self.data_dir / filename
        
        self.speak("Recording voice memo. Start speaking now.")
        
        # Record audio
        if pyaudio:
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024
            )
            
            frames = []
            for i in range(0, int(44100 / 1024 * duration)):
                data = stream.read(1024)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Save to file
            with wave.open(str(filepath), 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(frames))
            
            self.speak("Voice memo saved successfully.")
            return str(filepath)
        else:
            raise PyvoiceError("PyAudio required for voice memo recording")
    
    def get_stats(self) -> Dict:
        """Get usage statistics."""
        total_profiles = len(self.voice_profiles)
        total_history = len(self.conversation_history)
        
        most_used_profile = None
        max_usage = 0
        for profile in self.voice_profiles.values():
            if profile.usage_count > max_usage:
                max_usage = profile.usage_count
                most_used_profile = profile.name
        
        return {
            'total_profiles': total_profiles,
            'total_history_items': total_history,
            'most_used_profile': most_used_profile,
            'current_profile': self.current_profile.name if self.current_profile else None,
            'custom_words': len(self.custom_dictionary),
            'data_directory': str(self.data_dir)
        }
    
    def export_data(self, filepath: str):
        """Export all data to JSON file."""
        data = {
            'profiles': {name: profile.to_dict() for name, profile in self.voice_profiles.items()},
            'custom_dictionary': self.custom_dictionary,
            'conversation_history': self.get_conversation_history(1000),
            'stats': self.get_stats(),
            'export_date': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def import_data(self, filepath: str):
        """Import data from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Import profiles
        if 'profiles' in data:
            for name, profile_data in data['profiles'].items():
                profile = VoiceProfile.from_dict(profile_data)
                self.add_profile(profile)
        
        # Import custom dictionary
        if 'custom_dictionary' in data:
            for word, pronunciation in data['custom_dictionary'].items():
                self.add_word(word, pronunciation)
    
    def cleanup(self):
        """Clean up resources."""
        if self.engine:
            self.engine.stop()
        
        self.recognizer.stop_listening()
        self.commands.stop_listening()


# Convenience functions for easy usage
def speak(text: str, voice: str = "female", **kwargs):
    """Quick text-to-speech function."""
    pv = Pyvoice()
    pv.set_profile(voice)
    pv.speak(text, **kwargs)

def listen(timeout: int = 5, language: str = "en-US") -> str:
    """Quick voice recognition function."""
    pv = Pyvoice()
    return pv.listen(timeout, language)

def create_male_voice() -> Pyvoice:
    """Create Pyvoice instance with male voice."""
    pv = Pyvoice()
    pv.set_profile("male")
    return pv

def create_female_voice() -> Pyvoice:
    """Create Pyvoice instance with female voice."""
    pv = Pyvoice()
    pv.set_profile("female")
    return pv

def get_available_voices() -> List[Dict]:
    """Get all available system voices."""
    pv = Pyvoice()
    return pv.get_available_voices()

def quick_conversation(callback: Callable[[str], str] = None):
    """Start a quick voice conversation."""
    pv = Pyvoice()
    pv.start_conversation(callback)
    return pv


# Package information
__version__ = "1.0.0"
__author__ = "Kodukulla.Phani Kumar"
__email__ = "phanikumark715@gmail.com"
__description__ = "Advanced voice processing package with 100% more functionalities"
__url__ = "https://github.com/kodukulla-phani-kumar/pyvoice"

# Export main classes and functions
__all__ = [
    'Pyvoice',
    'VoiceProfile',
    'VoiceRecognizer',
    'VoiceCommands',
    'AudioProcessor',
    'PyvoiceError',
    'speak',
    'listen',
    'create_male_voice',
    'create_female_voice',
    'get_available_voices',
    'quick_conversation'
]