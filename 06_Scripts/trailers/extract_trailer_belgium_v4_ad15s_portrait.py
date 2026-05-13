#!/usr/bin/env python3
"""
extract_trailer_belgium_v4_ad15s_portrait.py
--------------------------------------------
Portrait 9:16 (1080x1920) version of the 15s ad cut, for YouTube Shorts /
TikTok / Reels paid placement.

Same timings as landscape ad15s. Built from a center crop of the landscape
master (608x1080 column → scaled to 1080x1920) — the piano shot is
camera-centered so a straight center crop preserves the subject.

Inputs:
  video → 02_Master_Mix/Moonlight Sonata MIXED_V3.mp4
  audio → 02_Master_Mix/Moonlight Sonata MIXED_FixedAudio.wav

Output:
  03_Cuts/Portrait/Moonlight Sonata TRAILER_BELGIUM_V4_AD15s_Portrait.mp4
"""

import subprocess, os, sys

INPUT_VIDEO = "../../02_Master_Mix/Moonlight Sonata MIXED_V3.mp4"
INPUT_AUDIO = "../../02_Master_Mix/Moonlight Sonata MIXED_FixedAudio.wav"
OUTPUT      = "../../03_Cuts/Portrait/Moonlight Sonata TRAILER_BELGIUM_V4_AD15s_Portrait.mp4"
START_TIME  = 230.0
DURATION    = 15.0

BEBAS = "/Users/lionelyu/Library/Fonts/BebasNeue-Regular.ttf"
MONT_BLACK = "/Users/lionelyu/Library/Fonts/Montserrat-Black.otf"

for f in (BEBAS, MONT_BLACK):
    if not os.path.exists(f):
        print(f"⚠️  Font not found: {f}")
        sys.exit(1)

WHITE = "white"
GOLD  = "#F5C518"
DIM   = "#AAAAAA"


def snap_alpha(start, end, attack=0.08, decay=0.4):
    a, b = start, end
    return (
        f"if(between(t\\,{a}\\,{b})\\,"
        f"if(lt(t\\,{a + attack})\\,(t-{a})/{attack}\\,"
        f"if(lt(t\\,{b - decay})\\,1\\,({b}-t)/{decay}))\\,0)"
    )


def dt(text, font, size, y_expr, start, end,
       attack=0.06, decay=0.35, borderw=3, color=WHITE,
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

# Center crop landscape → 9:16 column, scale to portrait
filters.append("crop=608:1080:656:0")
filters.append("scale=1080:1920:flags=lanczos")

# Grade + vignette (no letterbox bars for portrait)
filters.append("eq=contrast=1.12:saturation=0.82:brightness=-0.04:gamma=0.93")
filters.append("colorbalance=rs=-0.04:gs=0.02:bs=0.06")
filters.append("vignette=PI/4")

# ── BEATS (same timings as landscape ad15s; sizes reduced for portrait) ──

filters.append(dt("ONE PIANO.",  BEBAS, 160, "(h-text_h)/2", 0.2, 3.0))
filters.append(dt("ONE NIGHT.",  BEBAS, 160, "(h-text_h)/2", 3.2, 5.8))

# Brand title — stacked
filters.append(dt("MOONLIGHT", BEBAS, 180, "(h-text_h)/2 - 150", 6.0, 10.5, borderw=5, color=GOLD))
filters.append(dt("SONATA",    BEBAS, 180, "(h-text_h)/2 + 120", 6.0, 10.5, borderw=5, color=GOLD))
filters.append(hline("(ih/2)+20", 6.3, 10.2, width=340, color=f"{GOLD}@0.5"))

# CTA end card — JUNE 11 dominant, venue below
filters.append(dt("JUNE 11  ·  19\\:30",             MONT_BLACK, 95, "780", 10.7, 14.5, borderw=3, color=GOLD))
filters.append(hline("950", 11.0, 14.3, width=380, color="white@0.35"))
filters.append(dt("THEATER MALPERTUIS  ·  ZAVENTEM", MONT_BLACK, 36, "980", 10.7, 14.5, borderw=1, color=DIM))

filters.append("fade=t=in:st=0:d=0.4")
filters.append(f"fade=t=out:st={DURATION - 1.0}:d=1.0")

vfilter = ",".join(filters)
afilter = f"afade=t=in:st=0:d=0.4,afade=t=out:st={DURATION - 1.0}:d=1.0"

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

print("\n📱🎯  GENERATING 15s AD PORTRAIT — 9:16 1080x1920...")
print(f"    Video:   {INPUT_VIDEO} @ {START_TIME}s → {START_TIME + DURATION}s")
print(f"    Audio:   {INPUT_AUDIO} @ {START_TIME}s → {START_TIME + DURATION}s")
print(f"    Output:  {OUTPUT}\n")
subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
print(f"\n✅  AD15s PORTRAIT COMPLETE! → {OUTPUT}")
