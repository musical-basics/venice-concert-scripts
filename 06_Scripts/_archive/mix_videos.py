#!/usr/bin/env python3
"""
mix_videos.py
-------------
Alternates Keyboard Shot / Wide Shot at random 3-5s intervals.
- Keyboard: no zoom, starts first
- Wide: slow zoom-in OR zoom-out (alternating), centered crop
- Audio: Wide Shot only (full uncut)
- Output: 60fps, ~14 Mbps to match originals
"""

import subprocess, random, math, sys, os, json

KEYBOARD = "../../01_Source_Footage/Moonlight Sonata Keyboard Shot.mov"
WIDE     = "../../01_Source_Footage/Moonlight Sonata Wide Shot.mov"
OUTPUT   = "../../02_Master_Mix/Moonlight Sonata MIXED.mp4"

# Configuration
SEED     = 42      # Change this to any number to get a different set of reproducible timings
FPS      = 60
ZOOM_MAX = 1.06    # 6% zoom, subtle and cinematic
W, H     = 1920, 1080

# ---------------------------------------------------------------------------
def probe(path):
    r = subprocess.run(
        ["ffprobe","-v","quiet","-print_format","json",
         "-show_streams","-show_format", path],
        capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    for s in d["streams"]:
        if s.get("codec_type") == "video":
            return {
                "duration": float(d["format"]["duration"]),
                "bitrate":  int(d["format"].get("bit_rate", 14_000_000)),
            }

info     = probe(WIDE)
# Cap duration at 5:50 (350s)
duration = min(info["duration"], 350.0)
bitrate  = info["bitrate"]
print(f"Wide Shot (capped): {duration:.2f}s  {bitrate/1e6:.2f} Mbps")

# ---------------------------------------------------------------------------
# Build cut schedule
print(f"Using random seed: {SEED}")
random.seed(SEED)
segments = []
t, use_kbd = 0.0, True
while t < duration:
    seg = min(random.uniform(3.0, 5.0), duration - t)
    if seg < 0.5: break
    segments.append(("keyboard" if use_kbd else "wide", t, seg))
    t += seg
    use_kbd = not use_kbd

print(f"\n{len(segments)} segments:")
for i,(src,start,dur) in enumerate(segments):
    print(f"  [{i:3d}] {src:8s}  {start:8.3f}s  +{dur:.3f}s")

# ---------------------------------------------------------------------------
# Count each source so we can split correctly
n_kbd  = sum(1 for s,_,_ in segments if s=="keyboard")
n_wide = sum(1 for s,_,_ in segments if s=="wide")

# Build filter_complex
# Strategy:
#   [0:v] → fps=60, split=N → k0,k1,...
#   [1:v] → fps=60, split=M → w0,w1,...
#   Each keyboard seg: trim → setpts → [segNv]
#   Each wide seg:     trim → setpts → scale(zoom) → crop → [segNv]
#   All segNv → concat → [outv]
#
# Using scale+crop instead of zoompan:
#   zoom-in:  scale to 1920*(1+0.06*t/dur) × 1080*(1+0.06*t/dur), crop center
#   zoom-out: scale to 1920*(1.06-0.06*t/dur) × ..., crop center
#   't' in scale eval=frame is the PTS (seconds) of the current frame.
#   After setpts=PTS-STARTPTS, t starts at 0 for each segment.

parts = []

# Split inputs
def split_label(prefix, n, i): return f"{prefix}{i}"

# setsar=1 applied per-segment (after crop) to normalize SAR uniformly at concat
if n_kbd == 1:
    parts.append(f"[0:v]fps={FPS}[k0]")
else:
    parts.append(f"[0:v]fps={FPS},split={n_kbd}" + "".join(f"[k{j}]" for j in range(n_kbd)))

if n_wide == 1:
    parts.append(f"[1:v]fps={FPS}[w0]")
else:
    parts.append(f"[1:v]fps={FPS},split={n_wide}" + "".join(f"[w{j}]" for j in range(n_wide)))

kbd_i, wide_i = 0, 0
zoom_in = True   # toggles each wide segment

for i, (src, start, seg_dur) in enumerate(segments):
    if src == "keyboard":
        parts.append(
            f"[k{kbd_i}]trim=start={start:.6f}:duration={seg_dur:.6f},"
            f"setpts=PTS-STARTPTS,setsar=1"
            f"[seg{i}v]"
        )
        kbd_i += 1
    else:
        # scale expression – t is PTS in seconds after setpts reset
        if zoom_in:
            sw = f"'iw*(1+{ZOOM_MAX-1:.4f}*t/{seg_dur:.6f})'"
            sh = f"'ih*(1+{ZOOM_MAX-1:.4f}*t/{seg_dur:.6f})'"
        else:
            sw = f"'iw*({ZOOM_MAX:.4f}-{ZOOM_MAX-1:.4f}*t/{seg_dur:.6f})'"
            sh = f"'ih*({ZOOM_MAX:.4f}-{ZOOM_MAX-1:.4f}*t/{seg_dur:.6f})'"
        zoom_in = not zoom_in

        parts.append(
            f"[w{wide_i}]trim=start={start:.6f}:duration={seg_dur:.6f},"
            f"setpts=PTS-STARTPTS,"
            f"scale=w={sw}:h={sh}:eval=frame,"
            f"crop={W}:{H}:'(iw-{W})/2':'(ih-{H})/2',"
            f"setsar=1"
            f"[seg{i}v]"
        )
        wide_i += 1

# Concatenate
n = len(segments)
parts.append("".join(f"[seg{i}v]" for i in range(n)) + f"concat=n={n}:v=1:a=0[joinedv]")

# Add Title Overlay at the beginning
# Fade in (0-1s), Visible (1-4s), Fade out (4-5s)
title_text = "Moonlight Sonata Nightmare - Venice 2023"
font_path = "/System/Library/Fonts/Helvetica.ttc"
parts.append(
    f"[joinedv]drawtext=text='{title_text}':fontfile={font_path}:fontsize=72:fontcolor=white:"
    f"x=(w-text_w)/2:y=(h-text_h)/2:"
    f"alpha='if(lt(t,1),t,if(lt(t,4),1,if(lt(t,5),1-(t-4),0)))':"
    f"shadowcolor=black:shadowx=2:shadowy=2[v1]"
)

# Add "Live in Belgium, June 11, 2026!" at 0:40 (40s)
# Fade in (40-41s), Visible (41-43s), Fade out (43-44s)
belgium_text = "Live in Belgium, June 11, 2026!"
parts.append(
    f"[v1]drawtext=text='{belgium_text}':fontfile={font_path}:fontsize=72:fontcolor=white:"
    f"x=(w-text_w)/2:y=(h-text_h)/2:"
    f"alpha='if(lt(t,40),0,if(lt(t,41),t-40,if(lt(t,43),1,if(lt(t,44),1-(t-43),0))))':"
    f"shadowcolor=black:shadowx=2:shadowy=2[v2]"
)

# Add "Nightmare Remix Begins." at 2:38 (158s)
# Fade in (158-159s), Visible (159-161s), Fade out (161-162s)
remix_text = "Nightmare Remix Begins."
parts.append(
    f"[v2]drawtext=text='{remix_text}':fontfile={font_path}:fontsize=72:fontcolor=white:"
    f"x=(w-text_w)/2:y=(h-text_h)/2:"
    f"alpha='if(lt(t,158),0,if(lt(t,159),t-158,if(lt(t,161),1,if(lt(t,162),1-(t-161),0))))':"
    f"shadowcolor=black:shadowx=2:shadowy=2[v3]"
)

# Final Video Fade Out starting at 5:48 (348s) for 2 seconds
parts.append(f"[v3]fade=t=out:st=348:d=2[outv]")

filter_complex = ";\n".join(parts)

filter_script = "/tmp/mix_filter.txt"
with open(filter_script, "w") as f:
    f.write(filter_complex)
print(f"\nFilter written: {filter_script}")

# ---------------------------------------------------------------------------
cmd = [
    "ffmpeg", "-y",
    "-i", KEYBOARD,
    "-i", WIDE,
    f"-/filter_complex", filter_script,
    "-map", "[outv]",
    # Wide Shot audio + Fade Out (start 348s, duration 2s)
    "-filter:a", "afade=t=out:st=348:d=2",
    "-map", "1:a",
    "-c:v", "libx264",
    "-preset", "fast",
    "-b:v", str(bitrate),
    "-maxrate", str(int(bitrate * 1.2)),
    "-bufsize", str(int(bitrate * 2)),
    "-r", str(FPS),
    "-c:a", "aac",
    "-b:a", "320k",
    "-t", "350",   # End at 5:50
    OUTPUT
]

print("Running ffmpeg (expect 15-30 min)…")
result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
if result.returncode != 0:
    print("❌ ffmpeg failed"); sys.exit(1)

# Verify
out = probe(OUTPUT)
size_mb = os.path.getsize(OUTPUT) / 1e6
print(f"\n✅ Done: {OUTPUT}")
print(f"   Duration: {out['duration']:.1f}s  Bitrate: {out['bitrate']/1e6:.2f} Mbps  Size: {size_mb:.1f} MB")
