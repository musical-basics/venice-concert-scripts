#!/usr/bin/env python3
"""
extract_trailer_belgium_v2_portrait.py
--------------------------------------
Portrait (9:16, 1080x1920) Belgium trailer for Instagram Reels.
Blurred background + sharp center video layout.
Same text beats as landscape V2, positions adapted for vertical.
"""

import subprocess, os, sys

INPUT = "../../02_Master_Mix/Moonlight Sonata MIXED_V3.mp4"
OUTPUT = "../../03_Cuts/Portrait/Moonlight Sonata TRAILER_BELGIUM_V2_PORTRAIT.mp4"
START_TIME = 230.0
DURATION = 45.0

# Canvas
W, H = 1080, 1920

# Fonts
BEBAS = "/Users/lionelyu/Library/Fonts/BebasNeue-Regular.ttf"
MONT_BLACK = "/Users/lionelyu/Library/Fonts/Montserrat-Black.otf"

for f in (BEBAS, MONT_BLACK):
    if not os.path.exists(f):
        print(f"⚠️  Font not found: {f}")
        sys.exit(1)

# Colours
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


def flash(hit_time, dur=0.12):
    return (
        f"drawbox=x=0:y=0:w=iw:h=ih:"
        f"color=white@0.85:t=fill:"
        f"enable='between(t,{hit_time},{hit_time + dur})'"
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


# ═══════════════════════════════════════════════════════════════════════
#  FILTER COMPLEX
# ═══════════════════════════════════════════════════════════════════════

# Compose: blurred bg + sharp center overlay
# Source is 1920x1080. Center video zoomed ~15% (scale 1242 wide, crop back to 1080x608)
compose = (
    "[0:v]split[bg][fg];"
    "[bg]scale=-1:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
    "gblur=sigma=30,"
    "eq=brightness=0.02:saturation=0.65[blurred];"
    "[fg]scale=1242:-2,crop=1080:608[sharp];"
    "[blurred][sharp]overlay=x=0:y=(main_h-overlay_h)/2[composed];"
)

# Post-composition filters on the 1080x1920 canvas
pf = []

# Subtle colour grade (keep it light — bg is already bright)
pf.append("eq=contrast=1.06:saturation=0.92:brightness=0.0:gamma=0.97")

# Vignette
pf.append("vignette=PI/5")

# ── TEXT BEATS (adapted for 1080x1920) ────────────────────────────────

# Opening — centered on screen
pf.append(flash(2.0))
pf.append(dt("A MOONLIGHT", BEBAS, 100, "850", 2.0, 5.5, attack=0.06, decay=0.35, borderw=3))
pf.append(dt("REIMAGINED",  BEBAS, 100, "960", 2.0, 5.5, attack=0.06, decay=0.35, borderw=3))

pf.append(flash(6.0))
pf.append(dt("ONE PIANO.", BEBAS, 130, "(h-text_h)/2", 6.0, 9.5, attack=0.06, decay=0.4, borderw=3))

pf.append(flash(10.0))
pf.append(dt("ONE NIGHT.", BEBAS, 130, "(h-text_h)/2", 10.0, 13.5, attack=0.06, decay=0.4, borderw=3))

# Artist name — upper blurred zone (centered in top zone, ~y=328 center)
pf.append(flash(16.0))
pf.append(dt("LIONEL", BEBAS, 180, "270", 16.0, 22.0, attack=0.10, decay=0.6, borderw=5))
pf.append(dt("YU",     BEBAS, 180, "460", 16.0, 22.0, attack=0.10, decay=0.6, borderw=5))
pf.append(hline("440", 16.3, 21.5, width=300, color="white@0.45"))

# Live in Belgium — center
pf.append(dt("LIVE IN BELGIUM", BEBAS, 120, "(h-text_h)/2", 22.5, 26.5, attack=0.10, decay=0.5, borderw=3, color=TEAL))

# Title card — gold, centered
pf.append(flash(28.5))
pf.append(dt("MOONLIGHT", BEBAS, 170, "810", 28.5, 36.0, attack=0.12, decay=0.6, borderw=5, color=GOLD))
pf.append(dt("SONATA",    BEBAS, 170, "1000", 28.5, 36.0, attack=0.12, decay=0.6, borderw=5, color=GOLD))
pf.append(hline("980", 29.0, 35.5, width=360, color=f"{GOLD}@0.5"))

# Venue block — lower blurred zone
pf.append(flash(36.5))
pf.append(dt("THEATER MALPERTUIS",        BEBAS,      100, "1330", 36.5, 43.0, attack=0.10, decay=0.8, borderw=3))
pf.append(hline("1440", 36.8, 42.5, width=280, color="white@0.35"))
pf.append(dt("CC DE FACTORIJ · ZAVENTEM", MONT_BLACK,  38, "1465", 36.5, 43.0, attack=0.10, decay=0.8, borderw=1, color=DIM))
pf.append(dt("JUNE 11  ·  19:30",         MONT_BLACK,  64, "1530", 36.5, 43.0, attack=0.10, decay=0.8, borderw=2, color=GOLD))
pf.append(dt("LIMITED TICKETS AVAILABLE",  MONT_BLACK,  32, "1620", 37.5, 43.0, attack=0.15, decay=0.8, borderw=1, color=GOLD))

# Fades
pf.append("fade=t=in:st=0:d=1.0")
pf.append(f"fade=t=out:st={DURATION - 2.5}:d=2.5")

vfilter_post = ",".join(pf)
afilter = f"afade=t=in:st=0:d=0.6,afade=t=out:st={DURATION - 2.5}:d=2.5"

filter_complex = f"{compose}[composed]{vfilter_post}[v];[0:a]{afilter}[a]"

cmd = [
    "ffmpeg", "-y",
    "-ss", str(START_TIME),
    "-t", str(DURATION),
    "-i", INPUT,
    "-filter_complex", filter_complex,
    "-map", "[v]", "-map", "[a]",
    "-c:v", "libx264", "-preset", "medium", "-b:v", "12000k", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "320k",
    OUTPUT,
]

print(f"\n🎬  GENERATING BELGIUM TRAILER V2 PORTRAIT (9:16, 45s)...")
print(f"    Source:  {INPUT} @ {START_TIME}s → {START_TIME + DURATION}s")
print(f"    Output:  {OUTPUT} ({W}x{H})\n")
subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
print(f"\n✅  PORTRAIT TRAILER COMPLETE! → {OUTPUT}")
