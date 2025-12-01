"""
Video Compositor - Combines scenes, audio, and timing into final video.

Uses MoviePy to:
- Synchronize scenes with audio
- Add transitions
- Combine multiple clips
- Export final video
"""

from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json


class VideoCompositor:
    """Compose final video from scenes and audio."""

    def __init__(
        self,
        output_dir: str = "output/video",
        resolution: Tuple[int, int] = (1920, 1080),
        fps: int = 30
    ):
        """
        Initialize video compositor.

        Args:
            output_dir: Output directory for videos
            resolution: Video resolution (width, height)
            fps: Frames per second
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.resolution = resolution
        self.fps = fps

        # Lazy import moviepy (heavy dependency)
        try:
            # Try new import structure (moviepy 2.0+)
            try:
                from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, VideoFileClip
            except ImportError:
                # Fall back to old import structure (moviepy 1.x)
                from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, VideoFileClip

            self.ImageClip = ImageClip
            self.AudioFileClip = AudioFileClip
            self.CompositeVideoClip = CompositeVideoClip
            self.concatenate_videoclips = concatenate_videoclips
            self.VideoFileClip = VideoFileClip

            # Transitions
            try:
                from moviepy.video.fx import fadein, fadeout
                self.fadein = fadein
                self.fadeout = fadeout
            except ImportError:
                # Older moviepy structure
                try:
                    from moviepy.video.fx.all import fadein, fadeout
                    self.fadein = fadein
                    self.fadeout = fadeout
                except ImportError:
                    # No transitions available
                    self.fadein = lambda clip, *args: clip
                    self.fadeout = lambda clip, *args: clip

        except ImportError as e:
            raise ImportError(f"MoviePy not installed or incompatible: pip install moviepy. Error: {e}")

    def create_clip_from_image(
        self,
        image_path: str,
        duration: float,
        audio_path: Optional[str] = None
    ):
        """
        Create a video clip from an image.

        Args:
            image_path: Path to image file
            duration: Clip duration in seconds
            audio_path: Optional audio file to attach

        Returns:
            MoviePy VideoClip
        """
        # MoviePy 2.x uses duration parameter in constructor
        try:
            clip = self.ImageClip(image_path, duration=duration)
        except TypeError:
            # Fall back to old API (MoviePy 1.x)
            clip = self.ImageClip(image_path).set_duration(duration)

        if audio_path:
            audio = self.AudioFileClip(audio_path)
            # Adjust duration to match audio if needed
            if audio.duration > duration:
                try:
                    clip = self.ImageClip(image_path, duration=audio.duration)
                except TypeError:
                    clip = self.ImageClip(image_path).set_duration(audio.duration)

            try:
                clip = clip.with_audio(audio)  # MoviePy 2.x
            except AttributeError:
                clip = clip.set_audio(audio)  # MoviePy 1.x

        return clip

    def create_scene_clip(
        self,
        scene_config: Dict,
        default_duration: float = 5.0
    ):
        """
        Create a clip from scene configuration.

        Args:
            scene_config: Dictionary with scene parameters
                {
                    'image': 'path/to/image.png',
                    'duration': 5.0,
                    'audio': 'path/to/audio.mp3',  # optional
                    'transition': 'fade'  # optional
                }
            default_duration: Default duration if not specified

        Returns:
            MoviePy VideoClip
        """
        image_path = scene_config.get('image')
        duration = scene_config.get('duration', default_duration)
        audio_path = scene_config.get('audio')
        transition = scene_config.get('transition')

        clip = self.create_clip_from_image(image_path, duration, audio_path)

        # Apply transitions
        if transition == 'fade':
            clip = self.fadein(clip, 0.5)
            clip = self.fadeout(clip, 0.5)

        return clip

    def compose_video(
        self,
        scenes: List[Dict],
        output_filename: str = "final_video.mp4",
        background_music: Optional[str] = None,
        bg_music_volume: float = 0.1
    ) -> str:
        """
        Compose final video from multiple scenes.

        Args:
            scenes: List of scene configurations
            output_filename: Output video filename
            background_music: Optional background music file
            bg_music_volume: Background music volume (0.0 to 1.0)

        Returns:
            Path to output video file
        """
        print(f"\n🎬 Composing video from {len(scenes)} scenes")
        print(f"{'='*60}")

        clips = []

        for i, scene in enumerate(scenes, 1):
            print(f"  [{i}/{len(scenes)}] Processing scene: {scene.get('title', 'Untitled')}")

            try:
                clip = self.create_scene_clip(scene)
                clips.append(clip)
            except Exception as e:
                print(f"    ⚠️  Warning: Failed to create clip for scene {i}: {e}")
                continue

        if not clips:
            raise Exception("No clips were successfully created")

        # Concatenate all clips
        print(f"\n  Concatenating {len(clips)} clips...")
        final_clip = self.concatenate_videoclips(clips, method="compose")

        # Add background music if provided
        if background_music:
            print(f"  Adding background music...")
            try:
                bg_audio = self.AudioFileClip(background_music)
                bg_audio = bg_audio.volumex(bg_music_volume)

                # Loop background music if video is longer
                if bg_audio.duration < final_clip.duration:
                    bg_audio = bg_audio.audio_loop(duration=final_clip.duration)
                else:
                    bg_audio = bg_audio.subclip(0, final_clip.duration)

                # Mix with existing audio
                if final_clip.audio:
                    from moviepy.audio.AudioClip import CompositeAudioClip
                    final_audio = CompositeAudioClip([final_clip.audio, bg_audio])
                    final_clip = final_clip.set_audio(final_audio)
                else:
                    final_clip = final_clip.set_audio(bg_audio)

            except Exception as e:
                print(f"    ⚠️  Warning: Failed to add background music: {e}")

        # Export video
        output_path = self.output_dir / output_filename
        print(f"\n  Exporting video to: {output_path}")
        print(f"  Resolution: {self.resolution[0]}x{self.resolution[1]} @ {self.fps}fps")
        print(f"  Duration: {final_clip.duration:.1f} seconds")

        # Get number of CPU cores
        import os
        num_cores = os.cpu_count() or 4

        # FFmpeg parameters for multi-threading
        ffmpeg_params = [
            '-threads', str(num_cores),
            '-preset', 'ultrafast',
            '-crf', '28',  # Lower quality = faster encoding
            '-tune', 'fastdecode'
        ]

        final_clip.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            ffmpeg_params=ffmpeg_params,
            threads=num_cores,
            logger=None  # Disable verbose output
        )

        # Clean up
        final_clip.close()
        for clip in clips:
            clip.close()

        print(f"\n✅ Video exported successfully: {output_path}")
        return str(output_path)

    def create_simple_video(
        self,
        image_paths: List[str],
        audio_paths: List[str],
        output_filename: str = "video.mp4"
    ) -> str:
        """
        Create a simple video from images and audio files.

        Args:
            image_paths: List of image file paths
            audio_paths: List of audio file paths (must match images)
            output_filename: Output video filename

        Returns:
            Path to output video
        """
        if len(image_paths) != len(audio_paths):
            raise ValueError("Number of images must match number of audio files")

        # Get audio durations
        try:
            from pydub import AudioSegment
            durations = []
            for audio_path in audio_paths:
                audio = AudioSegment.from_file(audio_path)
                durations.append(len(audio) / 1000.0)  # ms to seconds
        except ImportError:
            print("⚠️  pydub not available, using default duration")
            durations = [5.0] * len(image_paths)

        # Create scene configs
        scenes = []
        for image_path, audio_path, duration in zip(image_paths, audio_paths, durations):
            scenes.append({
                'image': image_path,
                'audio': audio_path,
                'duration': duration,
                'transition': 'fade'
            })

        return self.compose_video(scenes, output_filename)

    def export_project_file(
        self,
        scenes: List[Dict],
        output_path: str = "output/project.json"
    ):
        """
        Export project configuration to JSON for later editing.

        Args:
            scenes: List of scene configurations
            output_path: Path to save project file
        """
        project = {
            'version': '1.0',
            'resolution': self.resolution,
            'fps': self.fps,
            'scenes': scenes
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(project, f, indent=2)

        print(f"✅ Project file saved: {output_path}")

    def load_project_file(self, project_path: str) -> List[Dict]:
        """
        Load project configuration from JSON.

        Args:
            project_path: Path to project file

        Returns:
            List of scene configurations
        """
        with open(project_path, 'r', encoding='utf-8') as f:
            project = json.load(f)

        self.resolution = tuple(project.get('resolution', self.resolution))
        self.fps = project.get('fps', self.fps)

        return project.get('scenes', [])


if __name__ == "__main__":
    # Test video composition
    print("Testing Video Compositor...\n")

    compositor = VideoCompositor()

    # Create a simple test video
    print("This test requires sample images and audio files.")
    print("To test the compositor, create some test files first:")
    print("  - Generate scenes with SceneGenerator")
    print("  - Generate audio with TTSGenerator")
    print("  - Then run this test with actual file paths")
