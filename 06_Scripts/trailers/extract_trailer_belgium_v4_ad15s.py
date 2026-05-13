#!/usr/bin/env python3
"""
extract_trailer_belgium_v4_ad15s.py
-----------------------------------
V4 — 15s ad cut for paid placement (Meta/TikTok/YT in-stream).
Hook → brand → CTA, no Lionel reveal, no "Live in Belgium" tension beat.
Compressed for skip-resistant viewing.

Beats (all timings in clip seconds):
  0.2 - 3.0   ONE PIANO.
  3.2 - 5.8   ONE NIGHT.
  6.0 - 10.5  MOONLIGHT / SONATA (stacked, gold)
  10.7 - 14.5 JUNE 11 · 19:30 + THEATER MALPERTUIS · ZAVENTEM
  14.0 - 15.0 fade out (audio + video)

Inputs:
  video → 02_Master_Mix/Moonlight Sonata MIXED_V3.mp4
  audio → 02_Master_Mix/Moonlight Sonata MIXED_FixedAudio.wav

Output:
  03_Cuts/Landscape/Moonlight Sonata TRAILER_BELGIUM_V4_AD15s.mp4
"""

import subprocess, os, sys

INPUT_VIDEO = "../../02_Master_Mix/Moonlight Sonata MIXED_V3.mp4"
INPUT_AUDIO = "../../02_Master_Mix/Moonlight Sonata MIXED_FixedAudio.wav"
OUTPUT      = "../../03_Cuts/Landscape/Moonlight Sonata TRAILER_BELGIUM_V4_AD15s.mp4"
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
filters.append("eq=contrast=1.12:saturation=0.82:brightness=-0.04:gamma=0.93")
filters.append("colorbalance=rs=-0.04:gs=0.02:bs=0.06")
filters.append("drawbox=x=0:y=0:w=iw:h=130:color=black@1:t=fill")
filters.append("drawbox=x=0:y=ih-130:w=iw:h=130:color=black@1:t=fill")
filters.append("vignette=PI/4.5")

# Hook beats — snappier attack/decay for 15s pacing
filters.append(dt("ONE PIANO.",  BEBAS, 200, "(h-text_h)/2", 0.2, 3.0))
filters.append(dt("ONE NIGHT.",  BEBAS, 200, "(h-text_h)/2", 3.2, 5.8))

# Brand title — stacked
filters.append(dt("MOONLIGHT", BEBAS, 240, "(h-text_h)/2 - 130", 6.0, 10.5, borderw=5, color=GOLD))
filters.append(dt("SONATA",    BEBAS, 240, "(h-text_h)/2 + 110", 6.0, 10.5, borderw=5, color=GOLD))
filters.append(hline("(ih/2)+10", 6.3, 10.2, width=400, color=f"{GOLD}@0.5"))

# CTA end card — JUNE 11 dominant, venue line below
filters.append(dt("JUNE 11  ·  19\\:30",       MONT_BLACK,  110, "430", 10.7, 14.5, borderw=3, color=GOLD))
filters.append(hline("570", 11.0, 14.3, width=420, color="white@0.35"))
filters.append(dt("THEATER MALPERTUIS  ·  ZAVENTEM", MONT_BLACK, 44, "590", 10.7, 14.5, borderw=1, color=DIM))

# Fades — tight to the 15s frame
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
    "-c:v", "libx264", "-preset", "medium", "-b:v", "16000k", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "320k",
    OUTPUT,
]

print("\n🎯  GENERATING 15s BELGIUM AD CUT — landscape...")
print(f"    Video:   {INPUT_VIDEO} @ {START_TIME}s → {START_TIME + DURATION}s")
print(f"    Audio:   {INPUT_AUDIO} @ {START_TIME}s → {START_TIME + DURATION}s")
print(f"    Output:  {OUTPUT}\n")
subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
print(f"\n✅  V4 AD CUT COMPLETE! → {OUTPUT}")
