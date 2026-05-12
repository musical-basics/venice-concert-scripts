#!/usr/bin/env python3
"""
mix_videos_v2.py
----------------
- BEAT SYNC: Analyzes audio to cut exactly on the 16th beat.
- CROSSFADES: Adds 0.3s smooth transitions between camera cuts.
- Reproducible SEED, Title Overlays, and 5:50 Truncation included.
"""

import subprocess, random, math, sys, os, json
import librosa
import numpy as np

KEYBOARD = "../../01_Source_Footage/Moonlight Sonata Keyboard Shot.mov"
WIDE     = "../../01_Source_Footage/Moonlight Sonata Wide Shot.mov"
OUTPUT   = "../../02_Master_Mix/Moonlight Sonata MIXED_V2.mp4"

# Configuration
SEED        = 42
FPS         = 60
ZOOM_MAX    = 1.06
W, H        = 1920, 1080
XFADE_DUR   = 0.3   # 0.3 second crossfade
BEATS_PER_CUT = 16  # Change cameras every 16 beats

# ---------------------------------------------------------------------------
def probe(path):
    r = subprocess.run(["ffprobe","-v","quiet","-print_format","json","-show_streams","-show_format",path], capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    for s in d["streams"]:
        if s.get("codec_type") == "video":
            return {"duration": float(d["format"]["duration"]), "bitrate": int(d["format"].get("bit_rate", 14_000_000))}

print("🎵 Analyzing audio for beats (this takes a moment)...")
y, sr = librosa.load(WIDE, sr=22050)
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beat_frames, sr=sr)

# Handle tempo being returned as an array or scalar
avg_tempo = float(np.mean(tempo))
print(f"Detected Tempo: {avg_tempo:.2f} BPM")

info     = probe(WIDE)
max_dur  = min(info["duration"], 350.0) # 5:50 limit
bitrate  = info["bitrate"]

# ---------------------------------------------------------------------------
# Build cut schedule based on beats
segments = []
t, use_kbd = 0.0, True
beat_idx = 0

while t < max_dur:
    # Find the time of the beat N steps ahead
    next_beat_idx = beat_idx + BEATS_PER_CUT
    if next_beat_idx >= len(beat_times):
        seg_end = max_dur
    else:
        seg_end = min(beat_times[next_beat_idx], max_dur)
    
    seg_dur = seg_end - t
    if seg_dur < 0.5: break
    
    segments.append(("keyboard" if use_kbd else "wide", t, seg_dur))
    
    t = seg_end
    beat_idx = next_beat_idx
    use_kbd = not use_kbd

print(f"\nCreated {len(segments)} beat-synced segments.")

# ---------------------------------------------------------------------------
# Build Filter Complex
parts = []
n_kbd  = sum(1 for s,_,_ in segments if s=="keyboard")
n_wide = sum(1 for s,_,_ in segments if s=="wide")

# Split inputs
if n_kbd > 1: parts.append(f"[0:v]fps={FPS},setsar=1,split={n_kbd}" + "".join(f"[k{j}]" for j in range(n_kbd)))
else: parts.append(f"[0:v]fps={FPS},setsar=1[k0]")

if n_wide > 1: parts.append(f"[1:v]fps={FPS},setsar=1,split={n_wide}" + "".join(f"[w{j}]" for j in range(n_wide)))
else: parts.append(f"[1:v]fps={FPS},setsar=1[w0]")

kbd_i, wide_i = 0, 0
zoom_in = True
seg_labels = []

for i, (src, start, seg_dur) in enumerate(segments):
    label = f"seg{i}v"
    if src == "keyboard":
        parts.append(f"[k{kbd_i}]trim=start={start:.6f}:duration={seg_dur+XFADE_DUR:.6f},setpts=PTS-STARTPTS,fps={FPS},setsar=1[v_{label}]")
        kbd_i += 1
    else:
        if zoom_in:
            sw, sh = f"iw*(1+{ZOOM_MAX-1:.4f}*t/{seg_dur:.6f})", f"ih*(1+{ZOOM_MAX-1:.4f}*t/{seg_dur:.6f})"
        else:
            sw, sh = f"iw*({ZOOM_MAX:.4f}-{ZOOM_MAX-1:.4f}*t/{seg_dur:.6f})", f"ih*({ZOOM_MAX:.4f}-{ZOOM_MAX-1:.4f}*t/{seg_dur:.6f})"
        zoom_in = not zoom_in
        parts.append(f"[w{wide_i}]trim=start={start:.6f}:duration={seg_dur+XFADE_DUR:.6f},setpts=PTS-STARTPTS,scale=w='{sw}':h='{sh}':eval=frame,crop={W}:{H}:(iw-{W})/2:(ih-{H})/2,fps={FPS},setsar=1[v_{label}]")
        wide_i += 1
    seg_labels.append(f"v_{label}")

# Chain XFADES
# FFmpeg xfade syntax: [a][b]xfade=transition=fade:duration=0.3:offset=OFFSET[out]
current_out = seg_labels[0]
total_offset = 0
for i in range(1, len(segments)):
    prev_dur = segments[i-1][2]
    total_offset += prev_dur
    next_label = f"xfade{i}"
    parts.append(f"[{current_out}][{seg_labels[i]}]xfade=transition=fade:duration={XFADE_DUR}:offset={total_offset:.6f}[{next_label}]")
    current_out = next_label

# Add Overlays
font_path = "/System/Library/Fonts/Helvetica.ttc"
parts.append(f"[{current_out}]drawtext=text='Moonlight Sonata Nightmare - Venice 2023':fontfile={font_path}:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:alpha='if(lt(t,1),t,if(lt(t,4),1,if(lt(t,5),1-(t-4),0)))':shadowcolor=black:shadowx=2:shadowy=2[v_title1]")
parts.append(f"[v_title1]drawtext=text='Live in Belgium, June 11, 2026!':fontfile={font_path}:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:alpha='if(lt(t,40),0,if(lt(t,41),t-40,if(lt(t,43),1,if(lt(t,44),1-(t-43),0))))':shadowcolor=black:shadowx=2:shadowy=2[v_title2]")
parts.append(f"[v_title2]drawtext=text='Nightmare Remix Begins.':fontfile={font_path}:fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:alpha='if(lt(t,158),0,if(lt(t,159),t-158,if(lt(t,161),1,if(lt(t,162),1-(t-161),0))))':shadowcolor=black:shadowx=2:shadowy=2[v_title3]")

# Final Video Fade Out at 5:48
parts.append(f"[v_title3]fade=t=out:st=348:d=2[outv]")

filter_script = "/tmp/mix_filter_v2.txt"
with open(filter_script, "w") as f: f.write(";\n".join(parts))

# ---------------------------------------------------------------------------
cmd = [
    "ffmpeg", "-y", "-i", KEYBOARD, "-i", WIDE,
    "-filter_complex_script", filter_script,
    "-map", "[outv]",
    "-filter:a", "afade=t=out:st=348:d=2", "-map", "1:a",
    "-c:v", "libx264", "-preset", "fast", "-b:v", str(bitrate), "-r", str(FPS),
    "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "320k", "-t", "350", OUTPUT
]

print("\n🚀 Running v2 (Beat Sync + Crossfades)... This will take a while.")
subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
print(f"\n✅ V2 Done! Output: {OUTPUT}")
