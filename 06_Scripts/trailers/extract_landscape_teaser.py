#!/usr/bin/env python3
"""
extract_landscape_teaser.py
---------------------------
Extracts the exact 60-second drop segment (2:30 to 3:30) from the Ultimate V3 Mix,
and adds the "Wait for the drop..." hype text and a clean fade-out.
"""

import subprocess, os

INPUT = "../../02_Master_Mix/Moonlight Sonata MIXED_V3.mp4"
OUTPUT = "../../03_Cuts/Landscape/Moonlight Sonata TEASER_LANDSCAPE_PART3_TEXT.mp4"
START_TIME = 230.0
DURATION = 45.0

font_path = "/System/Library/Fonts/Helvetica.ttc"
text = "Live in Belgium, June 11th!"

# Escape the comma in the text for FFmpeg
text_escaped = text.replace(",", "\\,")

# Alpha expressions for fading in and out
# Occurrence 1: 9s (fade in) -> 10s (hold) -> 13s (fade out) -> 14s
alpha1 = "if(between(t\\,9\\,14)\\, if(lt(t\\,10)\\, t-9\\, if(lt(t\\,13)\\, 1\\, 14-t))\\, 0)"
# Occurrence 2: 29s (fade in) -> 30s (hold) -> 33s (fade out) -> 34s
alpha2 = "if(between(t\\,29\\,34)\\, if(lt(t\\,30)\\, t-29\\, if(lt(t\\,33)\\, 1\\, 34-t))\\, 0)"

text1 = f"drawtext=text='{text_escaped}':fontfile={font_path}:fontsize=64:fontcolor=white:x=(w-text_w)/2:y=h-200:shadowcolor=black:shadowx=3:shadowy=3:alpha='{alpha1}'"
text2 = f"drawtext=text='{text_escaped}':fontfile={font_path}:fontsize=64:fontcolor=white:x=(w-text_w)/2:y=h-200:shadowcolor=black:shadowx=3:shadowy=3:alpha='{alpha2}'"

fade_out = f"fade=t=out:st={DURATION-2}:d=2"

cmd = [
    "ffmpeg", "-y", 
    "-ss", str(START_TIME),
    "-t", str(DURATION),
    "-i", INPUT,
    "-filter_complex", f"[0:v]{text1},{text2},{fade_out}[v];[0:a]afade=t=out:st={DURATION-2}:d=2[a]",
    "-map", "[v]", "-map", "[a]",
    "-c:v", "libx264", "-preset", "fast", "-b:v", "15000k", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "320k", 
    OUTPUT
]

print("\\n🚀 GENERATING LANDSCAPE 60S TEASER...")
subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
print(f"\\n✅ LANDSCAPE TEASER COMPLETE! Output: {OUTPUT}")
