"""
Video Generator - Main orchestrator for the video production pipeline.

Coordinates:
1. Script parsing
2. Scene generation
3. Voiceover generation
4. Video composition

Usage:
    from video_generator import VideoGenerator

    generator = VideoGenerator()
    video_path = generator.generate_from_script("scripts/my_script.md")
"""

import os
from pathlib import Path
from typing import Optional, Dict, List
import json

from parsers.script_parser import ScriptParser
from visuals.scene_generator import SceneGenerator
from audio.tts_generator import TTSGenerator
from video.compositor import VideoCompositor
from utils.llm_client import LLMClient


class VideoGenerator:
    """Main video generation orchestrator."""

    def __init__(
        self,
        output_dir: str = "output",
        tts_provider: str = "system",
        resolution: tuple = (1920, 1080),
        fps: int = 30,
        use_llm_for_scenes: bool = True,
        llm_endpoint: Optional[str] = None
    ):
        """
        Initialize video generator.

        Args:
            output_dir: Root output directory
            tts_provider: TTS provider ('system', 'elevenlabs', 'gtts')
            resolution: Video resolution (width, height)
            fps: Frames per second
            use_llm_for_scenes: Use LLM to intelligently generate scenes
            llm_endpoint: LLM API endpoint for scene generation
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.scenes_dir = self.output_dir / "scenes"
        self.audio_dir = self.output_dir / "audio"
        self.video_dir = self.output_dir / "video"

        # Initialize components
        self.scene_generator = SceneGenerator(
            output_dir=str(self.scenes_dir),
            resolution=resolution
        )

        self.tts_generator = TTSGenerator(
            provider=tts_provider,
            output_dir=str(self.audio_dir)
        )

        self.compositor = VideoCompositor(
            output_dir=str(self.video_dir),
            resolution=resolution,
            fps=fps
        )

        # LLM client for intelligent scene generation
        self.use_llm_for_scenes = use_llm_for_scenes
        if use_llm_for_scenes:
            endpoint = llm_endpoint or os.getenv('LLM_ENDPOINT', 'http://localhost:8439/v1')
            self.llm_client = LLMClient(endpoint=endpoint)
        else:
            self.llm_client = None

    def generate_from_script(
        self,
        script_path: str,
        output_filename: Optional[str] = None,
        skip_audio: bool = False,
        skip_video: bool = False
    ) -> Dict[str, any]:
        """
        Generate video from a markdown script.

        Args:
            script_path: Path to markdown script file
            output_filename: Optional custom output filename
            skip_audio: Skip audio generation (testing)
            skip_video: Skip video composition (testing)

        Returns:
            Dictionary with paths to generated assets
        """
        print(f"\n{'='*70}")
        print(f"🎬 VIDEO GENERATION PIPELINE")
        print(f"{'='*70}")
        print(f"Script: {script_path}")
        print(f"Output: {self.output_dir}")
        print(f"{'='*70}\n")

        # Step 1: Parse Script
        print("📜 STEP 1: Parsing Script")
        print("-" * 70)
        parser = ScriptParser(script_path)
        segments = parser.parse()
        parser.print_summary()

        if not segments:
            raise Exception("No segments found in script")

        # Step 2: Generate Scenes
        print(f"\n🎨 STEP 2: Generating Visual Scenes")
        print("-" * 70)
        scene_paths = self._generate_scenes_for_segments(segments)

        # Step 3: Generate Audio
        audio_paths = []
        if not skip_audio:
            print(f"\n🎤 STEP 3: Generating Voiceovers")
            print("-" * 70)
            audio_paths = self._generate_audio_for_segments(segments)

        # Step 4: Compose Video
        video_path = None
        if not skip_video and not skip_audio:
            print(f"\n🎬 STEP 4: Composing Final Video")
            print("-" * 70)

            if not output_filename:
                script_name = Path(script_path).stem
                output_filename = f"{script_name}_video.mp4"

            video_path = self._compose_video(segments, scene_paths, audio_paths, output_filename)

        # Summary
        print(f"\n{'='*70}")
        print(f"✅ VIDEO GENERATION COMPLETE")
        print(f"{'='*70}")

        result = {
            'script': script_path,
            'segments': len(segments),
            'scenes': scene_paths,
            'audio': audio_paths,
            'video': video_path,
            'output_dir': str(self.output_dir)
        }

        # Save manifest
        manifest_path = self.output_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n📋 Manifest saved: {manifest_path}")

        return result

    def _generate_scenes_for_segments(self, segments: List) -> List[str]:
        """Generate visual scenes for all segments."""
        scene_paths = []

        for i, segment in enumerate(segments, 1):
            print(f"\n  [{i}/{len(segments)}] {segment.title}")

            # Determine scene type from screen descriptions
            scene_type = self._classify_scene_type(segment)
            print(f"      Type: {scene_type}")

            # Generate appropriate scene
            if scene_type == "chart":
                scene_path = self._generate_chart_scene(segment, i)
            elif scene_type == "diagram":
                scene_path = self._generate_diagram_scene(segment, i)
            elif scene_type == "title":
                scene_path = self._generate_title_scene(segment, i)
            else:
                scene_path = self._generate_text_scene(segment, i)

            scene_paths.append(scene_path)
            print(f"      ✓ Saved: {Path(scene_path).name}")

        return scene_paths

    def _classify_scene_type(self, segment) -> str:
        """Classify what type of scene to generate based on screen descriptions."""
        screen_text = " ".join(segment.screen).lower()

        if "chart" in screen_text or "price" in screen_text or "graph" in screen_text:
            return "chart"
        elif "diagram" in screen_text or "flow" in screen_text or "comparison" in screen_text or "split screen" in screen_text:
            return "diagram"
        elif "title card" in screen_text or segment.start_time == 0:
            return "title"
        else:
            return "text"

    def _generate_chart_scene(self, segment, index: int) -> str:
        """Generate a chart scene."""
        title = segment.title.split("]")[-1].strip() if "]" in segment.title else segment.title

        # Extract annotations from screen descriptions
        annotations = []
        for screen in segment.screen:
            if len(screen) < 100:  # Short descriptions become annotations
                annotations.append(screen)

        scene_path = self.scenes_dir / f"scene_{index:02d}_chart.png"

        return self.scene_generator.generate_chart_scene(
            title=title,
            annotations=annotations[:3],  # Max 3 annotations
            output_path=str(scene_path)
        )

    def _generate_diagram_scene(self, segment, index: int) -> str:
        """Generate a diagram scene."""
        title = segment.title.split("]")[-1].strip() if "]" in segment.title else segment.title

        # Determine diagram type
        screen_text = " ".join(segment.screen).lower()
        if "vs" in screen_text or "comparison" in screen_text or "split" in screen_text:
            diagram_type = "comparison"
        elif "flow" in screen_text or "→" in screen_text:
            diagram_type = "flow"
        else:
            diagram_type = "framework"

        # Extract elements from screen descriptions
        elements = []
        for screen in segment.screen:
            # Simple extraction - split by punctuation
            parts = screen.replace("→", "|").split("|")
            elements.extend([p.strip() for p in parts if p.strip()])

        scene_path = self.scenes_dir / f"scene_{index:02d}_diagram.png"

        return self.scene_generator.generate_diagram_scene(
            title=title,
            diagram_type=diagram_type,
            elements=elements[:6],  # Max 6 elements
            output_path=str(scene_path)
        )

    def _generate_title_scene(self, segment, index: int) -> str:
        """Generate a title card scene."""
        title = segment.title.split("]")[-1].strip() if "]" in segment.title else segment.title

        # Use first voiceover line as subtitle if short
        subtitle = None
        if segment.voiceover and len(segment.voiceover[0]) < 60:
            subtitle = segment.voiceover[0]

        scene_path = self.scenes_dir / f"scene_{index:02d}_title.png"

        return self.scene_generator.generate_title_card(
            title=title,
            subtitle=subtitle,
            output_path=str(scene_path)
        )

    def _generate_text_scene(self, segment, index: int) -> str:
        """Generate a text overlay scene."""
        # Use first screen description or segment title
        text = segment.screen[0] if segment.screen else segment.title

        # Truncate if too long
        if len(text) > 80:
            text = text[:77] + "..."

        scene_path = self.scenes_dir / f"scene_{index:02d}_text.png"

        return self.scene_generator.generate_text_overlay(
            text=text,
            position="center",
            output_path=str(scene_path)
        )

    def _generate_audio_for_segments(self, segments: List) -> List[str]:
        """Generate voiceover audio for all segments."""
        # Prepare batch
        audio_segments = []
        for i, segment in enumerate(segments, 1):
            segment_id = f"segment_{i:02d}"
            text = segment.voiceover_text
            audio_segments.append((segment_id, text))

        # Generate batch
        audio_paths = self.tts_generator.generate_batch(audio_segments, show_progress=True)

        return audio_paths

    def _compose_video(
        self,
        segments: List,
        scene_paths: List[str],
        audio_paths: List[str],
        output_filename: str
    ) -> str:
        """Compose final video from scenes and audio."""

        # Build scene configurations
        scenes = []
        for i, (segment, scene_path, audio_path) in enumerate(zip(segments, scene_paths, audio_paths)):
            scenes.append({
                'title': segment.title,
                'image': scene_path,
                'audio': audio_path,
                'duration': segment.duration,
                'transition': 'fade'
            })

        # Export project file for manual editing if needed
        project_path = self.output_dir / "project.json"
        self.compositor.export_project_file(scenes, str(project_path))

        # Compose video
        video_path = self.compositor.compose_video(
            scenes=scenes,
            output_filename=output_filename
        )

        return video_path


if __name__ == "__main__":
    # Example usage
    print("Video Generator - Main Orchestrator\n")

    # Check if script exists
    script_path = "scripts/script_01_markets_dont_move_on_news_v2_global.md"

    if not Path(script_path).exists():
        print(f"❌ Script not found: {script_path}")
        print("\nTo use the video generator:")
        print("1. Place your script in the scripts/ directory")
        print("2. Run: python -m src.video_generator")
        exit(1)

    # Initialize generator
    generator = VideoGenerator(
        tts_provider="system",  # Use macOS built-in TTS
        use_llm_for_scenes=False  # Disable LLM for now
    )

    # Generate video
    try:
        result = generator.generate_from_script(
            script_path=script_path,
            skip_video=True  # Skip video composition for now (testing)
        )

        print("\n✨ Generation complete!")
        print(f"\nGenerated assets:")
        print(f"  - Scenes: {len(result['scenes'])}")
        print(f"  - Audio: {len(result['audio'])}")
        print(f"  - Output: {result['output_dir']}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
