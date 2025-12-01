"""
Script Parser - Extracts structured data from markdown video scripts.

Parses the custom script format with:
- Timestamps [0:00-0:20]
- [SCREEN]: Visual descriptions
- (VOICEOVER): Audio content
- {EDITING NOTE}: Production notes
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ScriptSegment:
    """A single segment of the video script."""
    start_time: float  # in seconds
    end_time: float    # in seconds
    title: str         # Section title
    screen: List[str]  # Visual descriptions
    voiceover: List[str]  # Voiceover text
    editing_notes: List[str]  # Editing notes

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    @property
    def voiceover_text(self) -> str:
        """Combined voiceover text for TTS."""
        return " ".join(self.voiceover)


class ScriptParser:
    """Parser for markdown video scripts."""

    # Regex patterns
    TIMESTAMP_PATTERN = r'\[(\d+):(\d+)-(\d+):(\d+)\]'
    SCREEN_PATTERN = r'\[SCREEN\]:\s*(.*?)(?=\(VOICEOVER\)|\{EDITING|$)'
    VOICEOVER_PATTERN = r'\(VOICEOVER\):\s*(.*?)(?=\[SCREEN\]|\{EDITING|$)'
    EDITING_PATTERN = r'\{EDITING[^}]*\}:\s*(.*?)(?=\[SCREEN\]|\(VOICEOVER\)|$)'

    def __init__(self, script_path: str):
        self.script_path = Path(script_path)
        self.raw_text = self._load_script()
        self.segments: List[ScriptSegment] = []

    def _load_script(self) -> str:
        """Load script from file."""
        with open(self.script_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _parse_timestamp(self, timestamp_str: str) -> Tuple[float, float]:
        """
        Parse timestamp string like '[0:20-0:50]' to (start_sec, end_sec).

        Returns:
            Tuple of (start_seconds, end_seconds)
        """
        match = re.search(self.TIMESTAMP_PATTERN, timestamp_str)
        if not match:
            raise ValueError(f"Invalid timestamp format: {timestamp_str}")

        start_min, start_sec, end_min, end_sec = map(int, match.groups())
        start_time = start_min * 60 + start_sec
        end_time = end_min * 60 + end_sec

        return start_time, end_time

    def _extract_sections(self) -> List[Dict]:
        """Extract script sections with timestamps and titles."""
        sections = []

        # Pattern to find sections with timestamps
        section_pattern = r'###\s*\[(\d+:\d+-\d+:\d+)\]\s*(.+?)(?=###|\Z)'

        for match in re.finditer(section_pattern, self.raw_text, re.DOTALL):
            timestamp_str = match.group(1)
            title = match.group(2).strip()
            content = match.group(0)

            # Find the code block with the actual script content
            code_block_match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
            if code_block_match:
                script_content = code_block_match.group(1)
            else:
                script_content = content

            sections.append({
                'timestamp_str': f"[{timestamp_str}]",
                'title': title,
                'content': script_content
            })

        return sections

    def _parse_section_content(self, content: str) -> Tuple[List[str], List[str], List[str]]:
        """
        Parse section content to extract screen, voiceover, and editing notes.

        Returns:
            Tuple of (screen_descriptions, voiceover_lines, editing_notes)
        """
        screen_descriptions = []
        voiceover_lines = []
        editing_notes = []

        # Extract all [SCREEN]: blocks
        screen_matches = re.finditer(r'\[SCREEN\]:\s*([^\n]+(?:\n(?!\[SCREEN\]|\(VOICEOVER\)|\{EDITING)[^\n]+)*)', content)
        for match in screen_matches:
            text = match.group(1).strip()
            if text:
                screen_descriptions.append(text)

        # Extract all (VOICEOVER): blocks
        voiceover_matches = re.finditer(r'\(VOICEOVER\):\s*([^\n]+(?:\n(?!\[SCREEN\]|\(VOICEOVER\)|\{EDITING)[^\n]+)*)', content)
        for match in voiceover_matches:
            text = match.group(1).strip()
            if text:
                voiceover_lines.append(text)

        # Extract all {EDITING}: blocks
        editing_matches = re.finditer(r'\{EDITING[^}]*\}:\s*([^\n]+)', content)
        for match in editing_matches:
            text = match.group(1).strip()
            if text:
                editing_notes.append(text)

        return screen_descriptions, voiceover_lines, editing_notes

    def parse(self) -> List[ScriptSegment]:
        """
        Parse the entire script into segments.

        Returns:
            List of ScriptSegment objects
        """
        sections = self._extract_sections()
        self.segments = []

        for section in sections:
            try:
                start_time, end_time = self._parse_timestamp(section['timestamp_str'])
                screen, voiceover, editing = self._parse_section_content(section['content'])

                segment = ScriptSegment(
                    start_time=start_time,
                    end_time=end_time,
                    title=section['title'],
                    screen=screen,
                    voiceover=voiceover,
                    editing_notes=editing
                )

                self.segments.append(segment)

            except Exception as e:
                print(f"Warning: Failed to parse section '{section['title']}': {e}")
                continue

        return self.segments

    def get_total_duration(self) -> float:
        """Get total video duration in seconds."""
        if not self.segments:
            return 0.0
        return max(seg.end_time for seg in self.segments)

    def export_voiceover_script(self, output_path: Optional[str] = None) -> str:
        """
        Export just the voiceover text for TTS generation.

        Args:
            output_path: Optional path to save voiceover text file

        Returns:
            Combined voiceover text
        """
        voiceover_parts = []

        for segment in self.segments:
            voiceover_parts.append(f"## {segment.title}")
            voiceover_parts.append(segment.voiceover_text)
            voiceover_parts.append("")  # Empty line between segments

        full_text = "\n".join(voiceover_parts)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_text)

        return full_text

    def print_summary(self):
        """Print a summary of the parsed script."""
        print(f"\n📜 Script Summary: {self.script_path.name}")
        print(f"{'='*60}")
        print(f"Total Duration: {self.get_total_duration():.1f} seconds ({self.get_total_duration()/60:.1f} minutes)")
        print(f"Number of Segments: {len(self.segments)}")
        print(f"\nSegments:")

        for i, seg in enumerate(self.segments, 1):
            print(f"\n{i}. [{seg.start_time:.0f}s - {seg.end_time:.0f}s] {seg.title}")
            print(f"   Duration: {seg.duration:.1f}s")
            print(f"   Screen descriptions: {len(seg.screen)}")
            print(f"   Voiceover length: {len(seg.voiceover_text)} chars")
            print(f"   Editing notes: {len(seg.editing_notes)}")


if __name__ == "__main__":
    # Test the parser
    script_path = "scripts/script_01_markets_dont_move_on_news_v2_global.md"

    parser = ScriptParser(script_path)
    segments = parser.parse()

    parser.print_summary()

    # Export voiceover text
    voiceover_text = parser.export_voiceover_script("output/voiceover_script.txt")
    print(f"\n✅ Voiceover script exported")
