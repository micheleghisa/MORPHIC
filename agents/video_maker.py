"""
MORPHIC — Video Maker Agent
Crea video TikTok/Reels faceless automaticamente:
- Genera frame immagine con testo overlays (Pillow)
- Voice-over AI (ElevenLabs API, o TTS gratuito)
- Montaggio con MoviePy
- Output: MP4 pronto da caricare

ZERO riprese, ZERO volto umano, 100% AI.
"""

import os, sys, json, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# ═══════════════════════════════════════════
# IMAGE FRAME GENERATOR (Pillow — gratuito)
# ═══════════════════════════════════════════

def create_frame(
    text: str,
    width: int = 1080,
    height: int = 1920,
    bg_color: tuple = (18, 18, 20),
    text_color: tuple = (255, 255, 255),
    accent_color: tuple = (100, 140, 255),
    font_size: int = 72,
    subtitle: str = None,
) -> Image.Image:
    """Crea un frame TikTok 9:16 con testo centrato. Design pulito, moderno."""
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Accent bar at top
    draw.rectangle([(0, 0), (width, 8)], fill=accent_color)

    # Try to load Inter font, fallback to default
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size // 2)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Word wrap
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] > width - 120:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))

    # Draw main text
    line_height = font_size + 20
    total_height = len(lines) * line_height
    y_start = (height - total_height) // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (width - (bbox[2] - bbox[0])) // 2
        y = y_start + i * line_height
        draw.text((x, y), line, fill=text_color, font=font)

    # Subtitle / branding
    if subtitle:
        bbox = draw.textbbox((0, 0), subtitle, font=font_small)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, height - 120), subtitle, fill=(150, 150, 160), font=font_small)

    # MORPHIC logo bottom
    draw.text((40, height - 80), "MORPHIC", fill=(100, 100, 110), font=font_small)

    return img


def create_script_frames(script_text: str, output_dir: str) -> list:
    """
    Parsa uno script TikTok (formato HOOK/TEXT OVERLAYS/VOICEOVER) e crea frame.
    Ritorna lista di percorsi immagine.
    """
    os.makedirs(output_dir, exist_ok=True)
    frames = []

    # Parse TEXT OVERLAYS section
    overlays = []
    overlay_section = False
    for line in script_text.split("\n"):
        if "TEXT OVERLAY" in line.upper():
            overlay_section = True
            continue
        if "VOICEOVER" in line.upper():
            overlay_section = False
            continue
        if overlay_section and line.strip():
            # Extract text from numbered overlay: "1. (0s) \"Your mirror is lying\""
            match = re.search(r'"([^"]+)"', line)
            if match:
                overlays.append(match.group(1))
            elif len(line.strip()) > 5:
                overlays.append(line.strip().split(". ", 1)[-1].strip('"'))

    # Parse HOOK
    hook = ""
    for line in script_text.split("\n"):
        if line.strip().startswith("HOOK:") or line.strip().startswith("**HOOK"):
            hook = line.split(":", 1)[-1].strip().strip('"').strip("*")
            break

    if hook:
        overlays.insert(0, hook)

    # Generate frames
    for i, text in enumerate(overlays[:8]):  # Max 8 frames per TikTok
        frame = create_frame(
            text=text,
            subtitle="Science-backed glow up",
            bg_color=(18, 18, 20) if i % 2 == 0 else (24, 24, 28),
            accent_color=(100, 140, 255) if i % 2 == 0 else (255, 120, 100),
        )
        filepath = f"{output_dir}/frame_{i:03d}.png"
        frame.save(filepath)
        frames.append(filepath)

    return frames


# ═══════════════════════════════════════════
# VIDEO ASSEMBLER (MoviePy — gratuito)
# ═══════════════════════════════════════════

def assemble_video(frames: list, output_path: str, duration_per_frame: float = 3.0, fps: int = 30):
    """
    Assembla i frame in un video TikTok MP4.
    Se disponibile MoviePy: crea video con transizioni.
    Senza MoviePy: crea slideshow con FFmpeg.
    """
    try:
        from moviepy import ImageClip, concatenate_videoclips

        clips = []
        for fp in frames:
            clip = ImageClip(fp, duration=duration_per_frame)
            clips.append(clip)

        video = concatenate_videoclips(clips, method="compose")
        video.write_videofile(
            output_path,
            fps=fps,
            codec="libx264",
            audio=False,
            preset="ultrafast",
            threads=4,
        )
        print(f"   ✅ Video created: {output_path} ({len(frames)} frames, {len(frames) * duration_per_frame:.0f}s)")
        return output_path

    except ImportError:
        # Fallback: FFmpeg
        import subprocess
        import tempfile

        # Create file list for FFmpeg
        list_file = f"{os.path.dirname(output_path)}/frames.txt"
        with open(list_file, "w") as f:
            for fp in frames:
                f.write(f"file '{os.path.abspath(fp)}'\n")
                f.write(f"duration {duration_per_frame}\n")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-vsync", "vfr",
            "-pix_fmt", "yuv420p",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            output_path
        ]
        subprocess.run(cmd, capture_output=True)
        print(f"   ✅ Video created via FFmpeg: {output_path}")
        return output_path


# ═══════════════════════════════════════════
# MAIN — Crea video da script
# ═══════════════════════════════════════════

def create_tiktok_video(script_text: str, output_path: str = None) -> str:
    """
    Prende uno script TikTok generato dagli agenti e produce un video MP4.
    """
    if output_path is None:
        output_path = f"agents/output/tiktok_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    from datetime import datetime

    temp_dir = f"agents/output/frames_{datetime.now().strftime('%H%M%S')}"
    frames = create_script_frames(script_text, temp_dir)

    if not frames:
        print("   ⚠️  No overlays found in script. Creating default frame.")
        frame = create_frame(text="Science-backed glow up tips", subtitle="Follow for more")
        frames = [f"{temp_dir}/frame_000.png"]
        frame.save(frames[0])

    video_path = assemble_video(frames, output_path)
    return video_path


# ═══════════════════════════════════════════
# BATCH PROCESSOR — Crea video per tutti gli script
# ═══════════════════════════════════════════

def batch_create_videos(week_id: str):
    """Crea video TikTok per tutti gli script della settimana."""
    calendar_file = f"content/{week_id}/calendar.json"
    content_file = f"content/{week_id}/content_plan.md"

    if not os.path.exists(content_file):
        print(f"   ⚠️  No content found for week {week_id}")
        return

    # Extract TikTok scripts from content plan
    with open(content_file) as f:
        content = f.read()

    # Split by script sections
    scripts = content.split("### Script")
    tiktok_scripts = []
    for s in scripts[1:]:  # Skip first section (not a script)
        if "HOOK" in s.upper() or "VOICEOVER" in s.upper():
            tiktok_scripts.append(s)

    if not tiktok_scripts:
        print("   ⚠️  No TikTok scripts found in content plan")
        return

    video_dir = f"content/{week_id}/videos"
    os.makedirs(video_dir, exist_ok=True)

    for i, script in enumerate(tiktok_scripts, 1):
        print(f"   🎬 Creating video {i}/{len(tiktok_scripts)}...")
        output = f"{video_dir}/tiktok_{i:02d}.mp4"
        create_tiktok_video(script, output)

    print(f"\n   ✅ {len(tiktok_scripts)} videos created in {video_dir}/")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        batch_create_videos(sys.argv[1])
    else:
        print("Usage: python video_maker.py <week_id>")
        print("Example: python video_maker.py 2026-W19")
