#!/usr/bin/env python3
"""
gen_yt_banner_v2.py
-------------------
YouTube channel banner (2560×1440) — artist-focused variant.
Leads with LIONEL YU as the hero, concert as supporting info.
All text within the 1546×423 mobile safe zone.
"""

import subprocess, os

INPUT = "../../02_Master_Mix/Moonlight Sonata MIXED_V3.mp4"
OUTPUT = "../../04_Graphics/Banners/YT_Banner_Belgium_V2.jpg"
FRAME_TIME = 242  # slightly different frame for variety

BEBAS = "/Users/lionelyu/Library/Fonts/BebasNeue-Regular.ttf"
MONT_BLACK = "/Users/lionelyu/Library/Fonts/Montserrat-Black.otf"

GOLD = "#F5C518"
WHITE = "white"
TEAL = "#4ECDC4"
DIM = "#AAAAAA"

BW, BH = 2560, 1440


def esc(text):
    return text.replace(":", "\\:").replace(",", "\\,").replace("'", "\\'")


def txt(text, font, size, color, x_expr, y, borderw=4, shadowx=4, shadowy=4):
    return (
        f"drawtext=text='{esc(text)}'"
        f":fontfile={font}:fontsize={size}:fontcolor={color}"
        f":borderw={borderw}:bordercolor=black@0.85"
        f":shadowcolor=black@0.5:shadowx={shadowx}:shadowy={shadowy}"
        f":x={x_expr}:y={y}"
    )


def hline(x, y, width, color="white@0.4"):
    return f"drawbox=x={x}:y={y}:w={width}:h=2:color={color}:t=fill"


filters = [
    # Scale to fill
    "scale=2560:1440:force_original_aspect_ratio=increase",
    "crop=2560:1440",

    # Cinematic grade
    "eq=contrast=1.12:saturation=0.80:brightness=-0.06:gamma=0.90",
    "colorbalance=rs=-0.04:gs=0.02:bs=0.08",

    # Vignette
    "vignette=PI/3.5",

    # Darken center band
    "drawbox=x=0:y=468:w=iw:h=503:color=black@0.45:t=fill",

    # ── ARTIST-FOCUSED TEXT ─────────────────────────────────────────────
    # Safe zone center: y=508..931, center_y=720

    # Hero: LIONEL YU
    txt("LIONEL YU", BEBAS, 170, WHITE, "(w-text_w)/2", 535, borderw=6, shadowx=6, shadowy=6),

    # Accent line
    hline("(iw-350)/2", 715, 350, f"{GOLD}@0.5"),

    # Sub: LIVE IN BELGIUM
    txt("LIVE IN BELGIUM", BEBAS, 80, GOLD, "(w-text_w)/2", 730, borderw=3, shadowx=3, shadowy=3),

    # Date
    txt("JUNE 11  ·  19:30", MONT_BLACK, 40, TEAL, "(w-text_w)/2", 825, borderw=2, shadowx=2, shadowy=2),

    # Venue
    txt("THEATERZAAL MALPERTUIS  ·  CC DE FACTORIJ  ·  ZAVENTEM", MONT_BLACK, 24, DIM, "(w-text_w)/2", 880, borderw=1, shadowx=2, shadowy=2),
]

vf = ",".join(filters)

cmd = [
    "ffmpeg", "-y",
    "-ss", str(FRAME_TIME),
    "-i", INPUT,
    "-frames:v", "1",
    "-vf", vf,
    "-q:v", "1",
    OUTPUT,
]

cwd = os.path.dirname(os.path.abspath(__file__))
print(f"\n🖼  Generating Artist-Focused YT Banner ({BW}×{BH})...")
subprocess.run(cmd, cwd=cwd)
print(f"\n✅  Banner V2 complete → {OUTPUT}")
