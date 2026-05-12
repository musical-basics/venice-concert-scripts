#!/usr/bin/env python3
"""
extract_trailer_belgium.py
--------------------------
Cinematic 45s trailer for the Belgium concert (June 11th).
Same drop segment as the landscape teaser, but with trailer-style fonts
(Bebas Neue / Montserrat Black), letterbox bars, color grade, and
hard punch-in text beats timed to the drop.
"""

import subprocess, os

INPUT = "../../02_Master_Mix/Moonlight Sonata MIXED_V3.mp4"
OUTPUT = "../../03_Cuts/Landscape/Moonlight Sonata TRAILER_BELGIUM.mp4"
START_TIME = 230.0
DURATION = 45.0

BEBAS = "/Users/lionelyu/Library/Fonts/BebasNeue-Regular.ttf"
MONT = "/Users/lionelyu/Library/Fonts/Montserrat-Black.otf"


def punch_alpha(start, end, attack=0.15, decay=0.35):
    """Snappy fade-in, hold, fade-out. Commas escaped for filter_complex."""
    a, b = start, end
    return (
        f"if(between(t\\,{a}\\,{b})\\,"
        f"if(lt(t\\,{a + attack})\\,(t-{a})/{attack}\\,"
        f"if(lt(t\\,{b - decay})\\,1\\,({b}-t)/{decay}))\\,0)"
    )


def drawtext(text, font, size, y_expr, start, end,
             attack=0.12, decay=0.4, borderw=2, color="white"):
    safe = text.replace("\\", "\\\\").replace(":", "\\:").replace(",", "\\,").replace("'", "\\'")
    alpha = punch_alpha(start, end, attack, decay)
    return (
        f"drawtext=text='{safe}':"
        f"fontfile={font}:"
        f"fontsize={size}:"
        f"fontcolor={color}:"
        f"borderw={borderw}:bordercolor=black@0.85:"
        f"shadowcolor=black@0.6:shadowx=3:shadowy=3:"
        f"x=(w-text_w)/2:y={y_expr}:"
        f"alpha='{alpha}'"
    )


# Trailer beats — paced to the drop. Drop hits ~0s of segment (start of climax).
# We open hard, breathe mid-trailer, then hit title + venue/date late.
beats = [
    # Cold-open punches (drop is already pumping)
    ("ONE NIGHT.",                BEBAS, 170, "(h-text_h)/2",        2.5,  6.0),
    ("ONE PIANO.",                BEBAS, 170, "(h-text_h)/2",        6.5, 10.0),
    ("ONE UNFORGETTABLE STORM.",  BEBAS, 110, "(h-text_h)/2",       10.5, 14.5),

    # Early venue establish — sets stakes before the title hit
    ("LIVE IN BELGIUM",           BEBAS, 150, "(h-text_h)/2",       15.5, 19.5, 0.15, 0.45, 3),

    # Visual breath 19.5 - 22s (let the music carry it)

    # Title card — stacked
    ("MOONLIGHT", BEBAS, 220, "(h-text_h)/2 - 120", 22.0, 30.0, 0.18, 0.5, 4),
    ("SONATA",    BEBAS, 220, "(h-text_h)/2 + 120", 22.0, 30.0, 0.18, 0.5, 4),

    # Reimagined tag
    ("REIMAGINED.", BEBAS, 130, "(h-text_h)/2", 30.5, 33.5),

    # End card — venue / city / date+time, all held together
    ("THEATER MALPERTUIS",         BEBAS, 130, "370", 34.0, 43.0, 0.18, 0.6, 3),
    ("CC DE FACTORIJ · ZAVENTEM",  BEBAS,  58, "525", 34.0, 43.0, 0.18, 0.6, 2),
    ("JUNE 11 · 19:30",            MONT,   90, "610", 34.0, 43.0, 0.18, 0.6, 3),
]

# Build filter chain
filters = []

# Cinematic color grade — slightly cooler, crushed, punchier
filters.append("eq=contrast=1.10:saturation=0.88:brightness=-0.03:gamma=0.95")

# Letterbox bars (1920x1080 -> 130px top/bottom for ~2.39:1-ish feel)
filters.append("drawbox=x=0:y=0:w=iw:h=130:color=black@1:t=fill")
filters.append("drawbox=x=0:y=ih-130:w=iw:h=130:color=black@1:t=fill")

# Subtle vignette via radial gradient sim (use vignette filter)
filters.append("vignette=PI/5")

# All trailer text beats
for beat in beats:
    filters.append(drawtext(*beat))

# Open from black, fade to black at end
filters.append("fade=t=in:st=0:d=1.2")
filters.append(f"fade=t=out:st={DURATION - 2.5}:d=2.5")

vfilter = ",".join(filters)
afilter = f"afade=t=in:st=0:d=0.4,afade=t=out:st={DURATION - 2.5}:d=2.5"

cmd = [
    "ffmpeg", "-y",
    "-ss", str(START_TIME),
    "-t", str(DURATION),
    "-i", INPUT,
    "-filter_complex", f"[0:v]{vfilter}[v];[0:a]{afilter}[a]",
    "-map", "[v]", "-map", "[a]",
    "-c:v", "libx264", "-preset", "medium", "-b:v", "16000k", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "320k",
    OUTPUT,
]

print("\n🎬  GENERATING BELGIUM TRAILER (45s landscape, cinematic)...")
subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
print(f"\n✅  TRAILER COMPLETE! Output: {OUTPUT}")
