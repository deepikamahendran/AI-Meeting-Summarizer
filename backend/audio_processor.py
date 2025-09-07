"""
Audio processing module for speech-to-text conversion
"""

import whisper
import tempfile
import os
from typing import Optional
import speech_recognition as sr
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self):
        try:
            # Initialize Whisper model
            from config import settings
            model_size = getattr(settings, 'WHISPER_MODEL', 'base')
            logger.info(f"Loading Whisper model: {model_size}")
            self.whisper_model = whisper.load_model(model_size)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            # Fallback to base model
            self.whisper_model = whisper.load_model("base")
        
        # Initialize speech recognition for fallback
        self.recognizer = sr.Recognizer()
    
    async def transcribe(self, audio_file_path: str) -> str:
        """
        Convert audio file to text using Whisper
        """
        try:
            logger.info(f"Starting Whisper transcription for: {audio_file_path}")
            
            # Primary: Use Whisper for transcription
            result = self.whisper_model.transcribe(
                audio_file_path,
                language="en",  # Force English for better accuracy
                task="transcribe",
                temperature=0.0,  # More deterministic output
                best_of=1,
                beam_size=1,
                patience=1.0,
                suppress_tokens=[-1],  # Suppress common noise tokens
                initial_prompt="This is a meeting recording with multiple speakers discussing business topics, tasks, and action items."
            )
            
            transcript = result["text"].strip()
            logger.info(f"Whisper transcription completed. Length: {len(transcript)} characters")
            
            if not transcript:
                raise Exception("Whisper returned empty transcript")
                
            return transcript
        
        except Exception as whisper_error:
            logger.error(f"Whisper transcription failed: {whisper_error}")
            
            # Fallback: Use speech_recognition library
            try:
                return await self._fallback_transcription(audio_file_path)
            except Exception as fallback_error:
                logger.error(f"Fallback transcription failed: {fallback_error}")
                raise Exception(f"All transcription methods failed. Whisper: {whisper_error}, Fallback: {fallback_error}")
    
    async def _fallback_transcription(self, audio_file_path: str) -> str:
        """
        Fallback transcription using speech_recognition library
        """
        logger.info("Using fallback transcription method")
        
        # Convert audio to WAV format if needed
        audio = AudioSegment.from_file(audio_file_path)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_wav:
            audio.export(tmp_wav.name, format="wav")
            
            try:
                with sr.AudioFile(tmp_wav.name) as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source)
                    
                    # Record audio data
                    audio_data = self.recognizer.record(source)
                    
                    # Use Google Speech Recognition
                    text = self.recognizer.recognize_google(audio_data)
                    logger.info(f"Fallback transcription completed. Length: {len(text)} characters")
                    return text
            
            finally:
                # Clean up temp file
                os.unlink(tmp_wav.name)
    
    def preprocess_audio(self, audio_file_path: str) -> str:
        """
        Preprocess audio for better transcription quality
        """
        try:
            logger.info("Preprocessing audio for better quality")
            
            # Load audio file
            audio = AudioSegment.from_file(audio_file_path)
            
            # Normalize audio
            normalized_audio = audio.normalize()
            
            # Remove silence from beginning and end
            trimmed_audio = normalized_audio.strip_silence(
                silence_threshold=-40,
                silence_chunk_len=1000,
                keep_silence=500
            )
            
            # Convert to mono if stereo
            if trimmed_audio.channels > 1:
                trimmed_audio = trimmed_audio.set_channels(1)
            
            # Set sample rate to 16kHz (optimal for speech recognition)
            trimmed_audio = trimmed_audio.set_frame_rate(16000)
            
            # Apply high-pass filter to remove low-frequency noise
            trimmed_audio = trimmed_audio.high_pass_filter(80)
            
            # Apply compression to even out volume levels
            trimmed_audio = trimmed_audio.compress_dynamic_range(threshold=-20.0, ratio=4.0, attack=5.0, release=50.0)
            
            # Save preprocessed audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                trimmed_audio.export(tmp_file.name, format="wav")
                logger.info(f"Audio preprocessing completed: {tmp_file.name}")
                return tmp_file.name
        
        except Exception as e:
            logger.warning(f"Audio preprocessing failed: {e}")
            return audio_file_path  # Return original if preprocessing fails
    
    def get_audio_info(self, audio_file_path: str) -> dict:
        """
        Get information about the audio file
        """
        try:
            audio = AudioSegment.from_file(audio_file_path)
            
            return {
                "duration": len(audio) / 1000.0,  # Duration in seconds
                "channels": audio.channels,
                "sample_rate": audio.frame_rate,
                "sample_width": audio.sample_width,
                "file_size": os.path.getsize(audio_file_path),
                "format": "audio"
            }
        
        except Exception as e:
            return {"error": f"Could not analyze audio file: {e}"}