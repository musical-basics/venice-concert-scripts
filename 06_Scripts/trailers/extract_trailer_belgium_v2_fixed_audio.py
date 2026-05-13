#!/usr/bin/env python3
"""
extract_trailer_belgium_v2_fixed_audio.py
-----------------------------------------
Same as extract_trailer_belgium_v2.py, but the audio is sourced from the
FIXED-audio WAV master instead of the MIXED_V3 mp4. Video chain is
identical; only the audio input + filter mapping changes.

Inputs:
  video → 02_Master_Mix/Moonlight Sonata MIXED_V3.mp4
  audio → 02_Master_Mix/Moonlight Sonata MIXED_FixedAudio.wav

Output:
  03_Cuts/Landscape/Moonlight Sonata TRAILER_BELGIUM_V2_FixedAudio.mp4
"""

import subprocess, os, sys

INPUT_VIDEO = "../../02_Master_Mix/Moonlight Sonata MIXED_V3.mp4"
INPUT_AUDIO = "../../02_Master_Mix/Moonlight Sonata MIXED_FixedAudio.wav"
OUTPUT      = "../../03_Cuts/Landscape/Moonlight Sonata TRAILER_BELGIUM_V2_FixedAudio.mp4"
START_TIME  = 230.0
DURATION    = 45.0

# ── Fonts ───────────────────────────────────────────────────────────────
BEBAS = "/Users/lionelyu/Library/Fonts/BebasNeue-Regular.ttf"
MONT_BLACK = "/Users/lionelyu/Library/Fonts/Montserrat-Black.otf"

for f in (BEBAS, MONT_BLACK):
    if not os.path.exists(f):
        print(f"⚠️  Font not found: {f}")
        sys.exit(1)

# ── Colour palette ──────────────────────────────────────────────────────
WHITE   = "white"
GOLD    = "#F5C518"     # IMDb-yellow / trailer gold
TEAL    = "#4ECDC4"     # accent for secondary beats
DIM     = "#AAAAAA"     # muted for small supporting text

# ── Helper: snap-in alpha (fast attack, slower decay) ───────────────────
def snap_alpha(start, end, attack=0.08, decay=0.5):
    """Quick punch-in, gentle bleed-out. All commas escaped."""
    a, b = start, end
    return (
        f"if(between(t\\,{a}\\,{b})\\,"
        f"if(lt(t\\,{a + attack})\\,(t-{a})/{attack}\\,"
        f"if(lt(t\\,{b - decay})\\,1\\,({b}-t)/{decay}))\\,0)"
    )

# ── Helper: white flash pulse (drawbox full-screen) ────────────────────
def flash(hit_time, dur=0.12):
    """Single-frame-ish white flash via drawbox alpha pulse."""
    return (
        f"drawbox=x=0:y=0:w=iw:h=ih:"
        f"color=white@0.85:t=fill:"
        f"enable='between(t,{hit_time},{hit_time + dur})'"
    )

# ── Helper: drawtext shorthand ──────────────────────────────────────────
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

# ── Helper: accent line (thin horizontal rule via drawbox) ──────────────
def hline(y, start, end, width=260, color="white@0.6"):
    return (
        f"drawbox=x=(iw-{width})/2:y={y}:w={width}:h=2:"
        f"color={color}:t=fill:"
        f"enable='between(t,{start},{end})'"
    )

# ═══════════════════════════════════════════════════════════════════════
#  FILTER CHAIN
# ═══════════════════════════════════════════════════════════════════════
filters = []

# 1. Cinematic colour grade — cool teal shadow push, slight contrast lift
filters.append("eq=contrast=1.12:saturation=0.82:brightness=-0.04:gamma=0.93")
filters.append("colorbalance=rs=-0.04:gs=0.02:bs=0.06")   # cool shadows

# 2. Letterbox bars (130px each → 2.39:1 feel on 1080p)
filters.append("drawbox=x=0:y=0:w=iw:h=130:color=black@1:t=fill")
filters.append("drawbox=x=0:y=ih-130:w=iw:h=130:color=black@1:t=fill")

# 3. Vignette
filters.append("vignette=PI/4.5")

# ── TEXT BEATS ──────────────────────────────────────────────────────────
# Opening — cold-open stinger punches
filters.append(flash(2.0))
filters.append(dt("A MOONLIGHT", BEBAS, 120, "(h-text_h)/2 - 40", 2.0, 5.5, attack=0.06, decay=0.35, borderw=3))
filters.append(dt("REIMAGINED",  BEBAS, 120, "(h-text_h)/2 + 80", 2.0, 5.5, attack=0.06, decay=0.35, borderw=3))

filters.append(flash(6.0))
filters.append(dt("ONE PIANO.",  BEBAS, 180, "(h-text_h)/2", 6.0, 9.5, attack=0.06, decay=0.4, borderw=3))

filters.append(flash(10.0))
filters.append(dt("ONE NIGHT.",  BEBAS, 180, "(h-text_h)/2", 10.0, 13.5, attack=0.06, decay=0.4, borderw=3))

# Mid-trailer breather (13.5 – 16s: let music carry)

# Artist name — big reveal
filters.append(flash(16.0))
filters.append(dt("LIONEL", BEBAS, 260, "(h-text_h)/2 - 130", 16.0, 22.0, attack=0.10, decay=0.6, borderw=5, color=WHITE))
filters.append(dt("YU",     BEBAS, 260, "(h-text_h)/2 + 100", 16.0, 22.0, attack=0.10, decay=0.6, borderw=5, color=WHITE))
filters.append(hline("(ih/2)+10", 16.3, 21.5, width=320, color="white@0.45"))

# Tension builder — subtitle
filters.append(dt("LIVE IN BELGIUM", BEBAS, 150, "(h-text_h)/2",
                  22.5, 26.5, attack=0.10, decay=0.5, borderw=3, color=TEAL))

# Second music breath (26.5 – 28.5s)

# Title card — MOONLIGHT SONATA in massive stacked type, held long
filters.append(flash(28.5))
filters.append(dt("MOONLIGHT", BEBAS, 240, "(h-text_h)/2 - 130", 28.5, 36.0, attack=0.12, decay=0.6, borderw=5, color=GOLD))
filters.append(dt("SONATA",    BEBAS, 240, "(h-text_h)/2 + 110", 28.5, 36.0, attack=0.12, decay=0.6, borderw=5, color=GOLD))
filters.append(hline("(ih/2)+10", 29.0, 35.5, width=400, color=f"{GOLD}@0.5"))

# End card — venue block (held to end)
filters.append(flash(36.5))
filters.append(dt("THEATER MALPERTUIS",        BEBAS,      120, "340",  36.5, 43.0, attack=0.10, decay=0.8, borderw=3))
filters.append(hline("465", 36.8, 42.5, width=300, color="white@0.35"))
filters.append(dt("CC DE FACTORIJ · ZAVENTEM", MONT_BLACK,  46, "485",  36.5, 43.0, attack=0.10, decay=0.8, borderw=1, color=DIM))
filters.append(dt("JUNE 11  ·  19:30",         MONT_BLACK,  80, "555",  36.5, 43.0, attack=0.10, decay=0.8, borderw=2, color=GOLD))
filters.append(dt("LIMITED TICKETS AVAILABLE",  MONT_BLACK,  38, "650",  37.5, 43.0, attack=0.15, decay=0.8, borderw=1, color=GOLD))

# ── FADES ───────────────────────────────────────────────────────────────
filters.append("fade=t=in:st=0:d=1.0")
filters.append(f"fade=t=out:st={DURATION - 2.5}:d=2.5")

vfilter = ",".join(filters)
afilter = f"afade=t=in:st=0:d=0.6,afade=t=out:st={DURATION - 2.5}:d=2.5"

# ═══════════════════════════════════════════════════════════════════════
#  ENCODE
# ═══════════════════════════════════════════════════════════════════════
# Two inputs: [0] video from MIXED_V3.mp4, [1] audio from MIXED_FixedAudio.wav
# Filter complex uses [0:v] for video, [1:a] for audio.
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

print("\n🎬  GENERATING BELGIUM TRAILER V2 (FIXED AUDIO) — 45s landscape...")
print(f"    Video:   {INPUT_VIDEO} @ {START_TIME}s → {START_TIME + DURATION}s")
print(f"    Audio:   {INPUT_AUDIO} @ {START_TIME}s → {START_TIME + DURATION}s")
print(f"    Output:  {OUTPUT}\n")
subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
print(f"\n✅  TRAILER V2 (FIXED AUDIO) COMPLETE! → {OUTPUT}")
