#!/usr/bin/env python3
"""
gen_thumbnails.py
-----------------
Generates two A/B landscape YouTube thumbnails (1920x1080) from the trailer.
Cinematic color grade, vignette, and bold trailer-style text.
"""

import subprocess, os

INPUT = "../../02_Master_Mix/Moonlight Sonata MIXED_V3.mp4"
FRAME_TIME = 245  # seconds into source — mid-drop, visually intense

BEBAS = "/Users/lionelyu/Library/Fonts/BebasNeue-Regular.ttf"
MONT_BLACK = "/Users/lionelyu/Library/Fonts/Montserrat-Black.otf"

GOLD = "#F5C518"
WHITE = "white"


def esc(text):
    return text.replace(":", "\\:").replace(",", "\\,").replace("'", "\\'")


def txt(text, font, size, color, y, borderw=5, shadowx=5, shadowy=5):
    return (
        f"drawtext=text='{esc(text)}'"
        f":fontfile={font}:fontsize={size}:fontcolor={color}"
        f":borderw={borderw}:bordercolor=black@0.85"
        f":shadowcolor=black@0.6:shadowx={shadowx}:shadowy={shadowy}"
        f":x=(w-text_w)/2:y={y}"
    )


# ── Shared base filters ────────────────────────────────────────────────
base = [
    "eq=contrast=1.15:saturation=0.85:brightness=-0.03:gamma=0.92",
    "colorbalance=rs=-0.04:gs=0.02:bs=0.06",
    "drawbox=x=0:y=0:w=iw:h=100:color=black@0.9:t=fill",
    "drawbox=x=0:y=ih-100:w=iw:h=100:color=black@0.9:t=fill",
    "vignette=PI/4",
    "drawbox=x=0:y=ih/2:w=iw:h=ih/2:color=black@0.4:t=fill",
]

# ── THUMBNAIL A ─────────────────────────────────────────────────────────
thumb_a = base + [
    txt("MOONLIGHT SONATA", BEBAS, 160, GOLD, 580),
    txt("REIMAGINED AS EDM", BEBAS, 120, WHITE, 740, borderw=4),
    txt("BELGIUM · JUNE 11", MONT_BLACK, 60, GOLD, 880, borderw=2, shadowx=3, shadowy=3),
]

# ── THUMBNAIL B ─────────────────────────────────────────────────────────
thumb_b = base + [
    txt("IN EXACTLY 1 MONTH", BEBAS, 150, WHITE, 540),
    txt("I PERFORM AN EPIC CONCERT", BEBAS, 130, WHITE, 700, borderw=4),
    txt("IN BELGIUM", BEBAS, 160, GOLD, 840),
]

thumbnails = [
    ("../../04_Graphics/Thumbnails/Thumbnail_A_Moonlight_EDM.jpg", thumb_a),
    ("../../04_Graphics/Thumbnails/Thumbnail_B_Epic_Concert.jpg",  thumb_b),
]

cwd = os.path.dirname(os.path.abspath(__file__))

for name, filters in thumbnails:
    vf = ",".join(filters)
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(FRAME_TIME),
        "-i", INPUT,
        "-frames:v", "1",
        "-vf", vf,
        "-q:v", "1",
        name,
    ]
    print(f"\n🖼  Generating {name}...")
    subprocess.run(cmd, cwd=cwd)
    print(f"    ✅ Done → {name}")

# Cleanup
raw = os.path.join(cwd, "_thumb_raw.jpg")
if os.path.exists(raw):
    os.remove(raw)

print("\n🎬  ALL THUMBNAILS COMPLETE!")
