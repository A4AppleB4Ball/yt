#!/usr/bin/env python3
"""
Quick test of the video generation pipeline.
Generates scenes and audio for first 3 segments only.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from video_generator import VideoGenerator

def main():
    print("\n" + "="*70)
    print("🧪 TESTING VIDEO GENERATION PIPELINE")
    print("="*70 + "\n")

    # Initialize generator
    generator = VideoGenerator(
        output_dir="output",
        tts_provider="system",
        use_llm_for_scenes=False
    )

    # Test with your markets script
    script_path = "scripts/script_01_markets_dont_move_on_news_v2_global.md"

    if not Path(script_path).exists():
        print(f"❌ Script not found: {script_path}")
        sys.exit(1)

    try:
        # Generate scenes and audio only (skip video for faster testing)
        print("📋 Generating scenes and audio (skipping video composition for speed)")
        print()

        result = generator.generate_from_script(
            script_path=script_path,
            skip_video=True  # Skip video composition for faster testing
        )

        print("\n" + "="*70)
        print("✅ TEST COMPLETE!")
        print("="*70)
        print(f"\nGenerated:")
        print(f"  🎨 {len(result['scenes'])} scene images")
        print(f"  🎤 {len(result['audio'])} audio files")
        print(f"\nOutput directory: {result['output_dir']}")
        print(f"\nTo view scenes:")
        print(f"  open {Path(result['output_dir']) / 'scenes'}")
        print(f"\nTo listen to audio:")
        print(f"  open {Path(result['output_dir']) / 'audio'}")
        print(f"\nTo generate full video:")
        print(f"  python generate_video.py {script_path}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
