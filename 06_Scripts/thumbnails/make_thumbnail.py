#!/usr/bin/env python3
"""
make_thumbnail.py
-----------------
Generates a YouTube thumbnail (1280x720) for the Belgium concert trailer.
Base frame: piano hands + blue stage beam from MIXED_V3 around 244s.
"""

import subprocess, os

INPUT = "../../05_Reference_Stills/screenshots/screenshot_4_244s.jpg"
OUTPUT = "../../04_Graphics/Thumbnails/Moonlight Sonata THUMBNAIL.jpg"

BEBAS = "/Users/lionelyu/Library/Fonts/BebasNeue-Regular.ttf"
MONT = "/Users/lionelyu/Library/Fonts/Montserrat-Black.otf"

vfilter = [
    # 1280x720, slight punch in color
    "scale=1280:720",
    "eq=contrast=1.18:saturation=1.15:brightness=-0.02:gamma=0.92",
    "vignette=PI/4.5",

    # Soft top-down dark gradient for title legibility (keeps the beam visible)
    "drawbox=x=0:y=0:w=iw:h=55:color=black@0.55:t=fill",
    "drawbox=x=0:y=55:w=iw:h=55:color=black@0.42:t=fill",
    "drawbox=x=0:y=110:w=iw:h=55:color=black@0.28:t=fill",
    "drawbox=x=0:y=165:w=iw:h=45:color=black@0.15:t=fill",

    # Title
    f"drawtext=text='MOONLIGHT SONATA':fontfile={BEBAS}:"
    f"fontsize=132:fontcolor=white:"
    f"borderw=5:bordercolor=black@0.95:"
    f"shadowcolor=black@0.85:shadowx=4:shadowy=4:"
    f"x=(w-text_w)/2:y=20",

    # Tagline (gold accent)
    f"drawtext=text='REIMAGINED AS EDM':fontfile={BEBAS}:"
    f"fontsize=60:fontcolor=0xffd86b:"
    f"borderw=3:bordercolor=black@0.95:"
    f"shadowcolor=black@0.7:shadowx=3:shadowy=3:"
    f"x=(w-text_w)/2:y=160",

    # Bottom-right red date badge
    "drawbox=x=830:y=620:w=430:h=80:color=0xcc1f1f@0.96:t=fill",
    "drawbox=x=830:y=620:w=430:h=80:color=white@0.85:t=2",
    f"drawtext=text='BELGIUM · JUNE 11':fontfile={MONT}:"
    f"fontsize=46:fontcolor=white:"
    f"borderw=2:bordercolor=black@0.85:"
    f"x=830+(430-text_w)/2:y=640",
]

cmd = [
    "ffmpeg", "-y",
    "-i", INPUT,
    "-frames:v", "1",
    "-vf", ",".join(vfilter),
    "-q:v", "2",
    OUTPUT,
]

print("\n🖼️   GENERATING YT THUMBNAIL...")
subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
print(f"\n✅  THUMBNAIL COMPLETE! Output: {OUTPUT}")
