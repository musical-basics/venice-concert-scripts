#!/usr/bin/env python3
"""
make_yt_banner.py
-----------------
YouTube channel banner (2560x1440) for the Belgium concert.

YT banner crop zones (centered):
  - TV:       2560 x 1440  (full canvas, only TV apps see the corners)
  - Desktop:  2560 x  423  (full width, ~middle band)
  - Tablet:   1855 x  423
  - Mobile:   1235 x  338  ← all critical text MUST live inside this box
                            x: 663-1897, y: 551-889
"""

import subprocess, os

INPUT = "../../05_Reference_Stills/screenshots/screenshot_4_244s.jpg"
OUTPUT = "../../04_Graphics/Banners/Moonlight Sonata YT_BANNER.jpg"

BEBAS = "/Users/lionelyu/Library/Fonts/BebasNeue-Regular.ttf"
MONT = "/Users/lionelyu/Library/Fonts/Montserrat-Black.otf"

vfilter = [
    # 1920x1080 source -> 2560x1440 (same 16:9, just upscale)
    "scale=2560:1440:flags=lanczos",
    # Cinematic grade
    "eq=contrast=1.15:saturation=1.12:brightness=-0.03:gamma=0.93",
    "vignette=PI/4.5",

    # Subtle horizontal dim band across the safe-zone vertical range
    # so text reads cleanly over the bright blue beam.
    "drawbox=x=0:y=535:w=iw:h=370:color=black@0.42:t=fill",

    # ---- Mobile-safe text block (y must stay 551..889) ----

    # TITLE  (y = 575..695)
    f"drawtext=text='MOONLIGHT SONATA':fontfile={BEBAS}:"
    f"fontsize=140:fontcolor=white:"
    f"borderw=5:bordercolor=black@0.95:"
    f"shadowcolor=black@0.85:shadowx=5:shadowy=5:"
    f"x=(w-text_w)/2:y=575",

    # TAGLINE  gold accent  (y = 720..775)
    f"drawtext=text='REIMAGINED AS EDM':fontfile={BEBAS}:"
    f"fontsize=64:fontcolor=0xffd86b:"
    f"borderw=3:bordercolor=black@0.95:"
    f"shadowcolor=black@0.7:shadowx=3:shadowy=3:"
    f"x=(w-text_w)/2:y=715",

    # FOOTER  date / city / time  (y = 815..865)
    f"drawtext=text='BELGIUM · JUNE 11 · 19\\:30':fontfile={MONT}:"
    f"fontsize=58:fontcolor=white:"
    f"borderw=3:bordercolor=black@0.9:"
    f"shadowcolor=black@0.7:shadowx=2:shadowy=2:"
    f"x=(w-text_w)/2:y=815",
]

cmd = [
    "ffmpeg", "-y",
    "-i", INPUT,
    "-frames:v", "1",
    "-vf", ",".join(vfilter),
    "-q:v", "2",
    OUTPUT,
]

print("\n🎨  GENERATING YT CHANNEL BANNER (2560x1440)...")
subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
print(f"\n✅  BANNER COMPLETE! Output: {OUTPUT}")
