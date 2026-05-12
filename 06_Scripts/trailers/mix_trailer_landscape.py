#!/usr/bin/env python3
"""
mix_trailer_landscape.py
------------------------
Extracts a 45-second segment and applies "Epic Trailer" effects:
- Cinematic letterboxing (2.35:1 aspect ratio crop)
- Slow-rising, dramatic text animations
- Bold, impactful typography
"""

import subprocess, os

INPUT = "../../02_Master_Mix/Moonlight Sonata MIXED_V3.mp4"
OUTPUT = "../../03_Cuts/Landscape/Moonlight Sonata EPIC_TRAILER.mp4"
START_TIME = 230.0
DURATION = 45.0

# Attempt to use Impact (classic trailer font), fallback to Avenir Next Heavy
font_path = "/System/Library/Fonts/Supplemental/Impact.ttf"
if not os.path.exists(font_path):
    font_path = "/System/Library/Fonts/Avenir Next.ttc"

# 1. Cinematic Crop (Convert 16:9 1920x1080 to 2.35:1 1920x816)
crop_filter = "crop=1920:816"

# 2. Epic Text Animations (Rising slowly while fading in/out)
# Text 1: 5s to 9s
text1 = f"drawtext=text='LIONEL YU':fontfile={font_path}:fontsize=140:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-((t-5)*15):shadowcolor=black:shadowx=5:shadowy=5:alpha='if(between(t\\,5\\,9)\\, if(lt(t\\,6)\\, t-5\\, if(lt(t\\,8)\\, 1\\, 9-t))\\, 0)'"

# Text 2: 15s to 20s
text2 = f"drawtext=text='LIVE IN BELGIUM':fontfile={font_path}:fontsize=160:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-((t-15)*15):shadowcolor=black:shadowx=6:shadowy=6:alpha='if(between(t\\,15\\,20)\\, if(lt(t\\,16)\\, t-15\\, if(lt(t\\,19)\\, 1\\, 20-t))\\, 0)'"

# Text 3: 30s to 36s (Climax color)
text3 = f"drawtext=text='JUNE 11':fontfile={font_path}:fontsize=200:fontcolor='#ffcc00':x=(w-text_w)/2:y=(h-text_h)/2-((t-30)*15):shadowcolor=black:shadowx=8:shadowy=8:alpha='if(between(t\\,30\\,36)\\, if(lt(t\\,31)\\, t-30\\, if(lt(t\\,35)\\, 1\\, 36-t))\\, 0)'"

# 3. Fade Out
fade_out = f"fade=t=out:st={DURATION-2}:d=2"

cmd = [
    "ffmpeg", "-y", 
    "-ss", str(START_TIME),
    "-t", str(DURATION),
    "-i", INPUT,
    "-filter_complex", f"[0:v]{crop_filter},{text1},{text2},{text3},{fade_out}[v];[0:a]afade=t=out:st={DURATION-2}:d=2[a]",
    "-map", "[v]", "-map", "[a]",
    "-c:v", "libx264", "-preset", "fast", "-b:v", "15000k", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "320k", 
    OUTPUT
]

print("\\n🚀 GENERATING EPIC TRAILER EDIT...")
subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
print(f"\\n✅ EPIC TRAILER COMPLETE! Output: {OUTPUT}")
