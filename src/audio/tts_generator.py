"""
TTS Generator - Generate voiceover audio from script text.

Supports multiple TTS providers:
- ElevenLabs (high quality, paid)
- gTTS (Google TTS, free but lower quality)
- System TTS (macOS 'say' command, free)
- LLM-based TTS (using your local LLM endpoint if supported)
"""

import os
from pathlib import Path
from typing import Optional, List
import subprocess
from abc import ABC, abstractmethod


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""

    @abstractmethod
    def generate(self, text: str, output_path: str) -> str:
        """Generate audio from text."""
        pass


class SystemTTS(TTSProvider):
    """macOS system TTS using 'say' command."""

    def __init__(self, voice: str = "Alex", rate: int = 180):
        """
        Initialize system TTS.

        Args:
            voice: Voice name (see 'say -v ?' for options)
            rate: Speech rate (words per minute)
        """
        self.voice = voice
        self.rate = rate

    def generate(self, text: str, output_path: str) -> str:
        """Generate audio using macOS 'say' command."""
        output_path = Path(output_path).with_suffix('.aiff')

        # Use 'say' to generate AIFF, then convert to WAV if needed
        cmd = [
            'say',
            '-v', self.voice,
            '-r', str(self.rate),
            '-o', str(output_path),
            text
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"    ✓ Generated audio: {output_path.name}")
            return str(output_path)
        except subprocess.CalledProcessError as e:
            raise Exception(f"System TTS failed: {e.stderr.decode()}")
        except FileNotFoundError:
            raise Exception("'say' command not found. This TTS provider only works on macOS.")


class ElevenLabsTTS(TTSProvider):
    """ElevenLabs TTS (requires API key)."""

    def __init__(self, api_key: Optional[str] = None, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        """
        Initialize ElevenLabs TTS.

        Args:
            api_key: ElevenLabs API key (or set ELEVEN_API_KEY env var)
            voice_id: Voice ID to use
        """
        self.api_key = api_key or os.getenv('ELEVEN_API_KEY')
        if not self.api_key:
            raise ValueError("ElevenLabs API key required (set ELEVEN_API_KEY env var)")

        self.voice_id = voice_id

        try:
            from elevenlabs import generate, set_api_key
            self.generate_func = generate
            set_api_key(self.api_key)
        except ImportError:
            raise ImportError("ElevenLabs package not installed: pip install elevenlabs")

    def generate(self, text: str, output_path: str) -> str:
        """Generate audio using ElevenLabs."""
        output_path = Path(output_path).with_suffix('.mp3')

        audio = self.generate_func(
            text=text,
            voice=self.voice_id,
            model="eleven_monolingual_v1"
        )

        with open(output_path, 'wb') as f:
            f.write(audio)

        print(f"    ✓ Generated audio: {output_path.name}")
        return str(output_path)


class GTTSProvider(TTSProvider):
    """Google TTS (free, lower quality)."""

    def __init__(self, lang: str = 'en', slow: bool = False):
        """
        Initialize gTTS.

        Args:
            lang: Language code
            slow: Use slow speech
        """
        self.lang = lang
        self.slow = slow

        try:
            from gtts import gTTS
            self.gTTS = gTTS
        except ImportError:
            raise ImportError("gTTS package not installed: pip install gtts")

    def generate(self, text: str, output_path: str) -> str:
        """Generate audio using gTTS."""
        output_path = Path(output_path).with_suffix('.mp3')

        tts = self.gTTS(text=text, lang=self.lang, slow=self.slow)
        tts.save(str(output_path))

        print(f"    ✓ Generated audio: {output_path.name}")
        return str(output_path)


class TTSGenerator:
    """Main TTS generator with provider management."""

    def __init__(
        self,
        provider: str = "system",
        output_dir: str = "output/audio",
        **provider_kwargs
    ):
        """
        Initialize TTS generator.

        Args:
            provider: TTS provider ('system', 'elevenlabs', 'gtts')
            output_dir: Output directory for audio files
            **provider_kwargs: Additional arguments for the provider
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize provider
        if provider == "system":
            self.provider = SystemTTS(**provider_kwargs)
        elif provider == "elevenlabs":
            self.provider = ElevenLabsTTS(**provider_kwargs)
        elif provider == "gtts":
            self.provider = GTTSProvider(**provider_kwargs)
        else:
            raise ValueError(f"Unknown TTS provider: {provider}")

        self.provider_name = provider

    def generate_voiceover(
        self,
        text: str,
        segment_id: str,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Generate voiceover audio for a script segment.

        Args:
            text: Text to convert to speech
            segment_id: Unique identifier for this segment
            output_filename: Optional custom filename

        Returns:
            Path to generated audio file
        """
        if not output_filename:
            output_filename = f"voiceover_{segment_id}.mp3"

        output_path = self.output_dir / output_filename

        # Generate audio
        audio_path = self.provider.generate(text, str(output_path))

        return audio_path

    def generate_batch(
        self,
        segments: List[tuple],
        show_progress: bool = True
    ) -> List[str]:
        """
        Generate voiceovers for multiple segments.

        Args:
            segments: List of (segment_id, text) tuples
            show_progress: Show progress messages

        Returns:
            List of generated audio file paths
        """
        audio_files = []

        if show_progress:
            print(f"\n🎤 Generating voiceovers using {self.provider_name.upper()} TTS")
            print(f"{'='*60}")

        for i, (segment_id, text) in enumerate(segments, 1):
            if show_progress:
                print(f"  [{i}/{len(segments)}] Segment: {segment_id}")

            # Clean text for TTS
            clean_text = self._clean_text_for_tts(text)

            # Generate audio
            audio_path = self.generate_voiceover(clean_text, segment_id)
            audio_files.append(audio_path)

        if show_progress:
            print(f"\n✅ Generated {len(audio_files)} voiceover files")

        return audio_files

    def _clean_text_for_tts(self, text: str) -> str:
        """
        Clean text for TTS generation.

        Remove markdown, fix formatting, etc.
        """
        # Remove markdown formatting
        text = text.replace('**', '').replace('*', '')
        text = text.replace('__', '').replace('_', '')

        # Remove code blocks
        import re
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`.*?`', '', text)

        # Clean up whitespace
        text = ' '.join(text.split())

        return text

    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get duration of audio file in seconds.

        Args:
            audio_path: Path to audio file

        Returns:
            Duration in seconds
        """
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0  # Convert ms to seconds
        except ImportError:
            raise ImportError("pydub package required: pip install pydub")


def list_available_voices():
    """List available system voices (macOS only)."""
    try:
        result = subprocess.run(['say', '-v', '?'], capture_output=True, text=True, check=True)
        print("Available macOS Voices:")
        print(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Unable to list voices. This feature is only available on macOS.")


if __name__ == "__main__":
    # Test TTS generation
    print("Testing TTS Generator...\n")

    # List available voices
    print("1. Checking available voices:")
    list_available_voices()

    # Test with system TTS
    print("\n2. Testing System TTS:")
    tts = TTSGenerator(provider="system", voice="Samantha", rate=175)

    test_text = """
    July 18th, 2025.
    The U.S. President signs the GENIUS Act into law.
    First comprehensive federal stablecoin regulation.
    The crypto industry calls it historic.
    """

    audio_path = tts.generate_voiceover(test_text, "test_segment")
    print(f"\n✅ Test audio generated: {audio_path}")

    # Get duration
    try:
        duration = tts.get_audio_duration(audio_path)
        print(f"   Duration: {duration:.2f} seconds")
    except ImportError:
        print("   (Install pydub to get audio duration)")
