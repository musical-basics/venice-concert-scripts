#!/usr/bin/env python3
"""
extract_trailer_belgium_v4_fixed_audio_portrait.py
--------------------------------------------------
Portrait 9:16 (1080x1920) version of V4 fixed-audio, for YouTube Shorts.

Same timings as landscape V4. Built from a center crop of the landscape
master (608x1080 column → scaled to 1080x1920). The piano shot is
camera-centered so a straight center crop preserves the subject.

Adaptations from landscape V4:
  • crop=608:1080:656:0 + scale=1080:1920 prepended
  • Letterbox bars dropped (portrait shorts fill the frame)
  • Text fontsizes reduced ~25-30% for the narrower 1080-wide frame
  • End-card y positions remapped to the 1920-tall canvas

Inputs:
  video → 02_Master_Mix/Moonlight Sonata MIXED_V3.mp4
  audio → 02_Master_Mix/Moonlight Sonata MIXED_FixedAudio.wav

Output:
  03_Cuts/Portrait/Moonlight Sonata TRAILER_BELGIUM_V4_FixedAudio_Portrait.mp4
"""

import subprocess, os, sys

INPUT_VIDEO = "../../02_Master_Mix/Moonlight Sonata MIXED_V3.mp4"
INPUT_AUDIO = "../../02_Master_Mix/Moonlight Sonata MIXED_FixedAudio.wav"
OUTPUT      = "../../03_Cuts/Portrait/Moonlight Sonata TRAILER_BELGIUM_V4_FixedAudio_Portrait.mp4"
START_TIME  = 230.0
DURATION    = 45.0

BEBAS = "/Users/lionelyu/Library/Fonts/BebasNeue-Regular.ttf"
MONT_BLACK = "/Users/lionelyu/Library/Fonts/Montserrat-Black.otf"

for f in (BEBAS, MONT_BLACK):
    if not os.path.exists(f):
        print(f"⚠️  Font not found: {f}")
        sys.exit(1)

WHITE = "white"
GOLD  = "#F5C518"
TEAL  = "#4ECDC4"
DIM   = "#AAAAAA"


def snap_alpha(start, end, attack=0.08, decay=0.5):
    a, b = start, end
    return (
        f"if(between(t\\,{a}\\,{b})\\,"
        f"if(lt(t\\,{a + attack})\\,(t-{a})/{attack}\\,"
        f"if(lt(t\\,{b - decay})\\,1\\,({b}-t)/{decay}))\\,0)"
    )


def dt(text, font, size, y_expr, start, end,
       attack=0.08, decay=0.5, borderw=2, color=WHITE,
       x_expr="(w-text_w)/2"):
    safe = (text.replace("\\", "\\\\")
                .replace(":", "\\:")
                .replace(",", "\\,")
                .replace("'", "\\'"))
    alpha = snap_alpha(start, end, attack, decay)
    return (
        f"drawtext=text='{safe}':"
        f"fontfile={font}:"
        f"fontsize={size}:"
        f"fontcolor={color}:"
        f"borderw={borderw}:bordercolor=black@0.85:"
        f"shadowcolor=black@0.55:shadowx=4:shadowy=4:"
        f"x={x_expr}:y={y_expr}:"
        f"alpha='{alpha}'"
    )


def hline(y, start, end, width=260, color="white@0.6"):
    return (
        f"drawbox=x=(iw-{width})/2:y={y}:w={width}:h=2:"
        f"color={color}:t=fill:"
        f"enable='between(t,{start},{end})'"
    )


filters = []

# 1. Center crop landscape → 9:16 column, scale to 1080x1920
filters.append("crop=608:1080:656:0")
filters.append("scale=1080:1920:flags=lanczos")

# 2. Same cinematic grade as landscape
filters.append("eq=contrast=1.12:saturation=0.82:brightness=-0.04:gamma=0.93")
filters.append("colorbalance=rs=-0.04:gs=0.02:bs=0.06")

# 3. Stronger vignette (portrait benefits from it)
filters.append("vignette=PI/4")

# ── TEXT BEATS (same timings as landscape v4; sizes reduced for portrait) ──

# Cold open at 0.3s (matches v4)
filters.append(dt("A MOONLIGHT", BEBAS,  95, "(h-text_h)/2 - 90", 0.3, 5.5, attack=0.08, decay=0.4, borderw=3))
filters.append(dt("REIMAGINED",  BEBAS,  95, "(h-text_h)/2 + 70", 0.3, 5.5, attack=0.08, decay=0.4, borderw=3))

filters.append(dt("ONE PIANO.",  BEBAS, 140, "(h-text_h)/2", 6.0, 9.5, attack=0.06, decay=0.4, borderw=3))
filters.append(dt("ONE NIGHT.",  BEBAS, 140, "(h-text_h)/2", 10.0, 13.5, attack=0.06, decay=0.4, borderw=3))

# Artist reveal
filters.append(dt("LIONEL", BEBAS, 200, "(h-text_h)/2 - 150", 16.0, 22.0, attack=0.10, decay=0.6, borderw=5, color=WHITE))
filters.append(dt("YU",     BEBAS, 200, "(h-text_h)/2 + 110", 16.0, 22.0, attack=0.10, decay=0.6, borderw=5, color=WHITE))
filters.append(hline("(ih/2)+20", 16.3, 21.5, width=280, color="white@0.45"))

# Tension builder
filters.append(dt("LIVE IN BELGIUM", BEBAS, 110, "(h-text_h)/2",
                  22.5, 26.5, attack=0.10, decay=0.5, borderw=3, color=TEAL))

# Title card — stacked
filters.append(dt("MOONLIGHT", BEBAS, 180, "(h-text_h)/2 - 150", 28.5, 36.0, attack=0.12, decay=0.6, borderw=5, color=GOLD))
filters.append(dt("SONATA",    BEBAS, 180, "(h-text_h)/2 + 120", 28.5, 36.0, attack=0.12, decay=0.6, borderw=5, color=GOLD))
filters.append(hline("(ih/2)+20", 29.0, 35.5, width=340, color=f"{GOLD}@0.5"))

# End card — remapped to 1920-tall canvas
filters.append(dt("THEATER MALPERTUIS",        BEBAS,       95, "640",  36.5, 43.0, attack=0.10, decay=0.8, borderw=3))
filters.append(hline("875", 36.8, 42.5, width=280, color="white@0.35"))
filters.append(dt("CC DE FACTORIJ · ZAVENTEM", MONT_BLACK,  38, "905",  36.5, 43.0, attack=0.10, decay=0.8, borderw=1, color=DIM))
filters.append(dt("JUNE 11  ·  19\\:30",       MONT_BLACK,  70, "1020", 36.5, 43.0, attack=0.10, decay=0.8, borderw=2, color=GOLD))
filters.append(dt("LIMITED TICKETS AVAILABLE", MONT_BLACK,  32, "1180", 37.5, 43.0, attack=0.15, decay=0.8, borderw=1, color=GOLD))

filters.append("fade=t=in:st=0:d=0.5")
filters.append(f"fade=t=out:st={DURATION - 2.5}:d=2.5")

vfilter = ",".join(filters)
afilter = f"afade=t=in:st=0:d=0.6,afade=t=out:st={DURATION - 2.5}:d=2.5"

cmd = [
    "ffmpeg", "-y",
    "-ss", str(START_TIME), "-t", str(DURATION), "-i", INPUT_VIDEO,
    "-ss", str(START_TIME), "-t", str(DURATION), "-i", INPUT_AUDIO,
    "-filter_complex", f"[0:v]{vfilter}[v];[1:a]{afilter}[a]",
    "-map", "[v]", "-map", "[a]",
    "-c:v", "libx264", "-preset", "medium", "-b:v", "12000k", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "320k",
    OUTPUT,
]

print("\n📱  GENERATING V4 PORTRAIT (FIXED AUDIO, EARLY OPENER) — 45s 9:16...")
print(f"    Video:   {INPUT_VIDEO} @ {START_TIME}s → {START_TIME + DURATION}s")
print(f"    Audio:   {INPUT_AUDIO} @ {START_TIME}s → {START_TIME + DURATION}s")
print(f"    Output:  {OUTPUT}\n")
subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
print(f"\n✅  V4 PORTRAIT COMPLETE! → {OUTPUT}")
