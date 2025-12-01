# Video Generation Pipeline - Setup Guide

## Overview

This is a complete YouTube video generation pipeline that transforms markdown scripts into professional videos with voiceovers, scenes, and animations.

## Architecture

```
Script (Markdown)
    ↓
Parser → Extract segments, timing, visuals, audio
    ↓
Scene Generator → Create charts, diagrams, title cards
    ↓
TTS Generator → Generate voiceover audio
    ↓
Video Compositor → Combine scenes + audio
    ↓
Final Video (MP4)
```

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install System Dependencies

#### macOS

```bash
# FFmpeg (required for video processing)
brew install ffmpeg

# ImageMagick (optional, for advanced image processing)
brew install imagemagick
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg imagemagick
```

### 3. TTS Setup

#### Option A: macOS System TTS (Default, Free)

No setup required! Uses built-in `say` command.

**List available voices:**
```bash
say -v '?'
```

**Recommended voices:**
- `Samantha` - Natural female voice
- `Alex` - Natural male voice
- `Daniel` - British English
- `Karen` - Australian English

#### Option B: ElevenLabs (High Quality, Paid)

1. Sign up at https://elevenlabs.io
2. Get your API key
3. Set environment variable:

```bash
export ELEVEN_API_KEY="your_api_key_here"
```

Or create a `.env` file:
```
ELEVEN_API_KEY=your_api_key_here
```

#### Option C: Google TTS (Free, Lower Quality)

No setup required. Uses `gtts` package.

## Quick Start

### 1. Test Scene Generation

```bash
cd src/visuals
python scene_generator.py
```

This creates test scenes in `output/scenes/`

### 2. Test TTS Generation

```bash
cd src/audio
python tts_generator.py
```

This creates test audio in `output/audio/`

### 3. Test Script Parser

```bash
cd src/parsers
python script_parser.py
```

### 4. Generate Full Video

```bash
python generate_video.py scripts/script_01_markets_dont_move_on_news_v2_global.md
```

## Usage

### Basic Usage

```bash
# Generate video with default settings (system TTS)
python generate_video.py scripts/my_script.md
```

### Advanced Options

```bash
# Use ElevenLabs TTS
python generate_video.py scripts/my_script.md --tts elevenlabs

# Custom resolution
python generate_video.py scripts/my_script.md --resolution 1280x720

# Custom FPS
python generate_video.py scripts/my_script.md --fps 60

# Custom output filename
python generate_video.py scripts/my_script.md -o my_video.mp4

# Skip video composition (generate scenes + audio only)
python generate_video.py scripts/my_script.md --skip-video

# Test scene generation only
python generate_video.py scripts/my_script.md --skip-audio --skip-video
```

## Script Format

Your markdown scripts should follow this format:

```markdown
# Script Title

## VISUAL & AUDIO PLAN

### [0:00-0:20] SECTION TITLE

\`\`\`
[SCREEN]: Visual description
(VOICEOVER):
The voiceover text goes here.

{EDITING NOTE}: Notes for editing
\`\`\`
```

**Key Components:**

- **Timestamps**: `[0:00-0:20]` - Start and end time
- **[SCREEN]**: Visual description (what to show)
- **(VOICEOVER)**: Text to speak (will be converted to audio)
- **{EDITING}**: Production notes (not included in video)

See `scripts/script_01_markets_dont_move_on_news_v2_global.md` for a complete example.

## Output Structure

```
output/
├── scenes/          # Generated scene images
│   ├── scene_01_title.png
│   ├── scene_02_chart.png
│   └── ...
├── audio/           # Generated voiceover audio
│   ├── voiceover_segment_01.mp3
│   ├── voiceover_segment_02.mp3
│   └── ...
├── video/           # Final video output
│   └── final_video.mp4
├── manifest.json    # Generation metadata
└── project.json     # Video project file (for manual editing)
```

## Customization

### Changing Visual Style

Edit `src/visuals/scene_generator.py`:

```python
# Style settings
self.bg_color = '#0a0a0a'      # Dark background
self.primary_color = '#FFD700'  # Gold
self.secondary_color = '#FF6B6B' # Red
self.accent_color = '#4ECDC4'   # Teal
```

### Changing TTS Voice (System TTS)

Edit `generate_video.py` or pass custom voice:

```python
generator = VideoGenerator(
    tts_provider="system",
    voice="Samantha",  # Custom voice
    rate=175           # Speech rate
)
```

### Adding Background Music

Modify `src/video/compositor.py` in `compose_video()`:

```python
video_path = self.compositor.compose_video(
    scenes=scenes,
    output_filename=output_filename,
    background_music="path/to/music.mp3",
    bg_music_volume=0.1  # 10% volume
)
```

## Troubleshooting

### "No module named 'moviepy'"

```bash
pip install moviepy
```

### "FFmpeg not found"

```bash
# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg
```

### "Permission denied" when generating audio (macOS)

Grant Terminal permission to use Speech:
1. System Preferences → Security & Privacy → Privacy
2. Select "Speech Recognition"
3. Enable Terminal/your IDE

### Video export is slow

Reduce resolution or FPS:
```bash
python generate_video.py scripts/my_script.md --resolution 1280x720 --fps 24
```

### Audio/video out of sync

Check that audio durations match expected segment durations. The system automatically adjusts video duration to match audio.

## Advanced Features

### Using LLM for Intelligent Scene Generation

If you have a local LLM endpoint running:

```bash
python generate_video.py scripts/my_script.md --llm-endpoint http://localhost:8439/v1
```

The system will use your LLM to:
- Analyze scene descriptions
- Generate better visual layouts
- Suggest scene types

### Manual Project Editing

After generation, edit `output/project.json` to fine-tune:
- Scene durations
- Transitions
- Scene order

Then regenerate video from project file.

## Performance Tips

1. **Scene Generation**: Fast (~1-2 seconds per scene)
2. **TTS Generation**:
   - System TTS: ~2-5 seconds per segment
   - ElevenLabs: ~5-10 seconds per segment (network dependent)
3. **Video Composition**: ~1-2 minutes for 7-8 minute video

**Total time for 7-8 minute video**: ~5-10 minutes

## Next Steps

1. Review generated scenes in `output/scenes/`
2. Listen to voiceovers in `output/audio/`
3. Watch final video in `output/video/`
4. Iterate on script and regenerate
5. Add custom background music
6. Export to YouTube

## Support

For issues or questions:
- Check existing examples in `scripts/`
- Review component tests in `src/*/test_*.py`
- See full README.md for channel philosophy and strategy
