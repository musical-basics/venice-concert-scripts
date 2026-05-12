#!/usr/bin/env python3
"""
make_yt_banner_artist.py
------------------------
YouTube channel banner (2560x1440) branded around the artist.
Subject sits right (in the desktop+TV bands), big "LIONEL YU" headline
sits left inside the 1235x338 mobile-safe rectangle.

Mobile-safe rectangle: x: 663..1897, y: 551..889
"""

import subprocess, os

INPUT = "../../05_Reference_Stills/v3_frames/v3_frame_1.jpg"  # artist + piano + blue beam
OUTPUT = "../../04_Graphics/Banners/Moonlight Sonata YT_BANNER_ARTIST.jpg"

BEBAS = "/Users/lionelyu/Library/Fonts/BebasNeue-Regular.ttf"
MONT = "/Users/lionelyu/Library/Fonts/Montserrat-Black.otf"

# Left margin inside mobile-safe (text x-anchor)
LX = 720

vfilter = [
    "scale=2560:1440:flags=lanczos",
    "eq=contrast=1.15:saturation=1.10:brightness=-0.04:gamma=0.93",
    "vignette=PI/4.5",

    # No dim panel — the source is naturally dark on the left.
    # Text relies on heavy outline + shadow for legibility.

    # ---- Mobile-safe text block ----

    # HEADLINE: artist name (left-aligned, x=LX)
    f"drawtext=text='LIONEL YU':fontfile={BEBAS}:"
    f"fontsize=180:fontcolor=white:"
    f"borderw=5:bordercolor=black@0.95:"
    f"shadowcolor=black@0.85:shadowx=5:shadowy=5:"
    f"x={LX}:y=565",

    # TAGLINE: brand line, gold accent
    f"drawtext=text='WHERE BEETHOVEN MEETS THE DROP':fontfile={BEBAS}:"
    f"fontsize=54:fontcolor=0xffd86b:"
    f"borderw=3:bordercolor=black@0.95:"
    f"shadowcolor=black@0.7:shadowx=3:shadowy=3:"
    f"x={LX}:y=735",

    # FOOTER: upcoming show
    f"drawtext=text='NEXT SHOW  ·  BELGIUM  ·  JUNE 11':fontfile={MONT}:"
    f"fontsize=44:fontcolor=white:"
    f"borderw=3:bordercolor=black@0.9:"
    f"shadowcolor=black@0.7:shadowx=2:shadowy=2:"
    f"x={LX}:y=820",
]

cmd = [
    "ffmpeg", "-y",
    "-i", INPUT,
    "-frames:v", "1",
    "-vf", ",".join(vfilter),
    "-q:v", "2",
    OUTPUT,
]

print("\n🎨  GENERATING ARTIST-BRANDED YT BANNER (2560x1440)...")
subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
print(f"\n✅  BANNER COMPLETE! Output: {OUTPUT}")
