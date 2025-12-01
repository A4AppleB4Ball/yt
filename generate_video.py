#!/usr/bin/env python3
"""
CLI for YouTube Video Generation Pipeline

Usage:
    python generate_video.py scripts/my_script.md
    python generate_video.py scripts/my_script.md --tts elevenlabs
    python generate_video.py scripts/my_script.md --skip-video
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from video_generator import VideoGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Generate YouTube videos from markdown scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate full video with system TTS
  python generate_video.py scripts/script_01.md

  # Use ElevenLabs TTS (requires API key)
  python generate_video.py scripts/script_01.md --tts elevenlabs

  # Generate only scenes and audio (skip video composition)
  python generate_video.py scripts/script_01.md --skip-video

  # Test scene generation only
  python generate_video.py scripts/script_01.md --skip-audio --skip-video

Available TTS Providers:
  system      - macOS built-in TTS (default, free)
  elevenlabs  - ElevenLabs TTS (high quality, requires API key)
  gtts        - Google TTS (free, lower quality)
        """
    )

    parser.add_argument(
        "script",
        help="Path to markdown script file"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output filename (default: auto-generated from script name)"
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help="Output directory (default: output/)"
    )

    parser.add_argument(
        "--tts",
        choices=["system", "elevenlabs", "gtts"],
        default="system",
        help="TTS provider (default: system)"
    )

    parser.add_argument(
        "--resolution",
        default="1920x1080",
        help="Video resolution (default: 1920x1080)"
    )

    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Frames per second (default: 30)"
    )

    parser.add_argument(
        "--skip-audio",
        action="store_true",
        help="Skip audio generation (testing)"
    )

    parser.add_argument(
        "--skip-video",
        action="store_true",
        help="Skip video composition (testing)"
    )

    parser.add_argument(
        "--llm-endpoint",
        help="LLM endpoint for intelligent scene generation"
    )

    args = parser.parse_args()

    # Validate script path
    script_path = Path(args.script)
    if not script_path.exists():
        print(f"❌ Error: Script not found: {script_path}")
        sys.exit(1)

    # Parse resolution
    try:
        width, height = map(int, args.resolution.split('x'))
        resolution = (width, height)
    except ValueError:
        print(f"❌ Error: Invalid resolution format: {args.resolution}")
        print("   Use format: WIDTHxHEIGHT (e.g., 1920x1080)")
        sys.exit(1)

    # Initialize generator
    print(f"\n🎬 Initializing Video Generator")
    print(f"   TTS Provider: {args.tts}")
    print(f"   Resolution: {resolution[0]}x{resolution[1]}")
    print(f"   FPS: {args.fps}")

    try:
        generator = VideoGenerator(
            output_dir=args.output_dir,
            tts_provider=args.tts,
            resolution=resolution,
            fps=args.fps,
            use_llm_for_scenes=bool(args.llm_endpoint),
            llm_endpoint=args.llm_endpoint
        )
    except Exception as e:
        print(f"\n❌ Error initializing generator: {e}")
        sys.exit(1)

    # Generate video
    try:
        result = generator.generate_from_script(
            script_path=str(script_path),
            output_filename=args.output,
            skip_audio=args.skip_audio,
            skip_video=args.skip_video
        )

        print(f"\n{'='*70}")
        print(f"✨ SUCCESS!")
        print(f"{'='*70}")
        print(f"\nGenerated assets:")
        print(f"  📁 Output directory: {result['output_dir']}")
        print(f"  🎨 Scenes: {len(result['scenes'])} files")

        if result['audio']:
            print(f"  🎤 Audio: {len(result['audio'])} files")

        if result['video']:
            print(f"  🎬 Video: {result['video']}")
            print(f"\n▶️  Play video:")
            print(f"     open {result['video']}")

        print(f"\n📋 Full manifest: {Path(result['output_dir']) / 'manifest.json'}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
