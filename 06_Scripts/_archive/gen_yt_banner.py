#!/usr/bin/env python3
"""
gen_yt_banner.py
----------------
YouTube channel banner (2560×1440) for the Belgium concert.
All key text lives in the center 1546×423 mobile safe zone.
Extended cinematic background fills the full TV canvas.
"""

import subprocess, os

INPUT = "../../02_Master_Mix/Moonlight Sonata MIXED_V3.mp4"
OUTPUT = "../../04_Graphics/Banners/YT_Banner_Belgium.jpg"
FRAME_TIME = 248  # dramatic mid-drop frame

BEBAS = "/Users/lionelyu/Library/Fonts/BebasNeue-Regular.ttf"
MONT_BLACK = "/Users/lionelyu/Library/Fonts/Montserrat-Black.otf"

GOLD = "#F5C518"
WHITE = "white"
TEAL = "#4ECDC4"
DIM = "#AAAAAA"

# YouTube banner dimensions
BW, BH = 2560, 1440
# Mobile safe zone: 1546×423, centered
SAFE_W, SAFE_H = 1546, 423
SAFE_X = (BW - SAFE_W) // 2   # 507
SAFE_Y = (BH - SAFE_H) // 2   # 508


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
    return (
        f"drawbox=x={x}:y={y}:w={width}:h=2"
        f":color={color}:t=fill"
    )


filters = [
    # Scale source to fill 2560×1440
    "scale=2560:1440:force_original_aspect_ratio=increase",
    "crop=2560:1440",

    # Cinematic grade
    "eq=contrast=1.12:saturation=0.80:brightness=-0.06:gamma=0.90",
    "colorbalance=rs=-0.04:gs=0.02:bs=0.08",

    # Strong vignette
    "vignette=PI/3.5",

    # Darken the center band for text readability
    f"drawbox=x=0:y={SAFE_Y - 40}:w=iw:h={SAFE_H + 80}:color=black@0.45:t=fill",

    # ── TEXT (all within safe zone) ─────────────────────────────────────
    # Safe zone: x=507..2053, y=508..931, center_x=1280, center_y=720

    # Title: MOONLIGHT SONATA — large, gold
    txt("MOONLIGHT SONATA", BEBAS, 130, GOLD, "(w-text_w)/2", 560, borderw=5, shadowx=5, shadowy=5),

    # Accent line below title
    hline("(iw-400)/2", 700, 400, f"{GOLD}@0.45"),

    # Tagline: REIMAGINED AS EDM
    txt("REIMAGINED AS EDM", BEBAS, 70, WHITE, "(w-text_w)/2", 715, borderw=3, shadowx=3, shadowy=3),

    # Date/Venue line
    txt("BELGIUM  ·  JUNE 11  ·  19:30", MONT_BLACK, 42, TEAL, "(w-text_w)/2", 810, borderw=2, shadowx=2, shadowy=2),

    # Venue detail
    txt("THEATERZAAL MALPERTUIS  ·  CC DE FACTORIJ  ·  ZAVENTEM", MONT_BLACK, 26, DIM, "(w-text_w)/2", 870, borderw=1, shadowx=2, shadowy=2),
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
print(f"\n🖼  Generating YouTube Banner ({BW}×{BH})...")
print(f"    Safe zone: {SAFE_W}×{SAFE_H} centered")
subprocess.run(cmd, cwd=cwd)
print(f"\n✅  Banner complete → {OUTPUT}")
