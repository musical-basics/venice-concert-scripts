#!/usr/bin/env python3
"""
mix_canon_in_dream_v3.py
------------------------
Canon in Dream — landscape master mix, V3 pipeline.

Mirrors mix_videos_v3.py (Moonlight Sonata) but tuned for Canon in Dream:
  • Sources: Canon in Dream Keyboard / Wide Shot (~299s)
  • Title overlay: "Canon in Dream - Venice 2023"
  • Belgium concert promo at 40-44s (same as Moonlight)
  • No "Nightmare Remix Begins" beat (Moonlight-specific, dropped)
  • Fade-out timing computed dynamically from source length

Same V3 pipeline features:
  - Multi-Cam PiP (Keyboard overlay on Wide)
  - Dynamic Bass Shake (kick detection)
  - Live audio waveform visualizer
  - Musical progress bar
  - Beat-synced cuts + crossfades
"""

import subprocess, os, json
import librosa
import numpy as np

KEYBOARD = "../../01_Source_Footage/Canon in Dream Keyboard Shot.mov"
WIDE     = "../../01_Source_Footage/Canon in Dream Wide Shot.mov"
OUTPUT   = "../../02_Master_Mix/Canon in Dream MIXED_V3.mp4"

# Configuration
SEED          = 42
FPS           = 60
ZOOM_MAX      = 1.06
W, H          = 1920, 1080
XFADE_DUR     = 0.3
BEATS_PER_CUT = 16
PIP_W, PIP_H  = 480, 270


def probe(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_streams", "-show_format", path],
        capture_output=True, text=True, check=True,
    )
    d = json.loads(r.stdout)
    for s in d["streams"]:
        if s.get("codec_type") == "video":
            return {
                "duration": float(d["format"]["duration"]),
                "bitrate":  int(d["format"].get("bit_rate", 14_000_000)),
            }


print("🎵 Deep Analysis: Detecting beats and bass hits...")
y, sr = librosa.load(WIDE, sr=22050)
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beat_frames, sr=sr)
avg_tempo = float(np.mean(tempo))

# Bass detection (< 150 Hz)
S = np.abs(librosa.stft(y))
bass_energy = np.mean(S[librosa.fft_frequencies(sr=sr) < 150], axis=0)
bass_onsets = librosa.onset.onset_detect(onset_envelope=bass_energy, sr=sr, units="time")

print(f"Tempo: {avg_tempo:.2f} BPM | Detected {len(bass_onsets)} Bass Hits.")

info       = probe(WIDE)
max_dur    = info["duration"]
bitrate    = info["bitrate"]
fade_start = max_dur - 2.0

# ---------------------------------------------------------------------------
# Cut schedule
segments = []
t, use_kbd = 0.0, True
beat_idx = 0
while t < max_dur:
    next_beat_idx = beat_idx + BEATS_PER_CUT
    seg_end = min(
        beat_times[next_beat_idx] if next_beat_idx < len(beat_times) else max_dur,
        max_dur,
    )
    seg_dur = seg_end - t
    if seg_dur < 0.5:
        break
    segments.append(("keyboard" if use_kbd else "wide", t, seg_dur))
    t, beat_idx, use_kbd = seg_end, next_beat_idx, not use_kbd

# ---------------------------------------------------------------------------
# Filter graph
parts = []

# 1. Prepare inputs
parts.append(f"[0:v]fps={FPS},setsar=1,split=2[k_master1][k_master2]")
parts.append(f"[1:v]fps={FPS},setsar=1,split=1[w_master1]")

# 2. PiP version
parts.append(f"[k_master1]scale={PIP_W}:{PIP_H}[k_pip]")

# 3. Split per segment
n_kbd  = sum(1 for s, _, _ in segments if s == "keyboard")
n_wide = sum(1 for s, _, _ in segments if s == "wide")

if n_kbd > 0:
    parts.append(f"[k_master2]split={n_kbd}" + "".join(f"[k{j}]" for j in range(n_kbd)))
if n_wide > 0:
    parts.append(f"[w_master1]split={n_wide}" + "".join(f"[w{j}]" for j in range(n_wide)))
    parts.append(f"[k_pip]split={n_wide}" + "".join(f"[kp{j}]" for j in range(n_wide)))

# 4. Process segments
kbd_i, wide_i = 0, 0
zoom_in = True
seg_labels = []

for i, (src, start, seg_dur) in enumerate(segments):
    label = f"seg{i}v"
    if src == "keyboard":
        parts.append(
            f"[k{kbd_i}]trim=start={start:.6f}:duration={seg_dur+XFADE_DUR:.6f},"
            f"setpts=PTS-STARTPTS,fps={FPS},setsar=1[v_{label}]"
        )
        kbd_i += 1
    else:
        if zoom_in:
            sw = f"iw*(1+{ZOOM_MAX-1:.4f}*t/{seg_dur:.6f})"
            sh = f"ih*(1+{ZOOM_MAX-1:.4f}*t/{seg_dur:.6f})"
        else:
            sw = f"iw*({ZOOM_MAX:.4f}-{ZOOM_MAX-1:.4f}*t/{seg_dur:.6f})"
            sh = f"ih*({ZOOM_MAX:.4f}-{ZOOM_MAX-1:.4f}*t/{seg_dur:.6f})"
        zoom_in = not zoom_in

        parts.append(
            f"[w{wide_i}]trim=start={start:.6f}:duration={seg_dur+XFADE_DUR:.6f},"
            f"setpts=PTS-STARTPTS,scale=w='{sw}':h='{sh}':eval=frame,"
            f"crop={W}:{H}:(iw-{W})/2:(ih-{H})/2,fps={FPS},setsar=1[w_base{i}]"
        )
        parts.append(
            f"[kp{wide_i}]trim=start={start:.6f}:duration={seg_dur+XFADE_DUR:.6f},"
            f"setpts=PTS-STARTPTS,fps={FPS},setsar=1[kp_trim{i}]"
        )
        parts.append(f"[w_base{i}][kp_trim{i}]overlay=x=W-w-50:y=50[v_{label}]")
        wide_i += 1
    seg_labels.append(f"v_{label}")

# 5. Chain crossfades
current_out = seg_labels[0]
total_offset = 0
for i in range(1, len(segments)):
    prev_dur = segments[i-1][2]
    total_offset += prev_dur
    next_label = f"xfade{i}"
    parts.append(
        f"[{current_out}][{seg_labels[i]}]xfade=transition=fade:"
        f"duration={XFADE_DUR}:offset={total_offset:.6f}[{next_label}]"
    )
    current_out = next_label

# 6. Bass shake
hits = [f"between(t\\,{o:.3f}\\,{o+0.1:.3f})" for o in bass_onsets if o < max_dur]
if len(hits) > 100:
    hits = hits[:100]
shake_expr = "0"
if len(hits) > 0:
    shake_expr = "5*(" + "+".join(hits) + ")"

parts.append(
    f"[{current_out}]scale={W+20}:{H+20},"
    f"crop={W}:{H}:"
    f"(iw-ow)/2+sin(t*100)*{shake_expr}:(ih-oh)/2+cos(t*100)*{shake_expr}[v_shaken]"
)
v_to_viz = "v_shaken"

# 7. Visualizer, progress bar, titles, fade out
parts.append(f"[1:a]showwaves=s=400x120:mode=line:colors=cyan@0.8:rate={FPS}[waves]")

font_path = "/System/Library/Fonts/Helvetica.ttc"
final_chain = [
    f"overlay=x=50:y={H-180}:eval=frame",
    f"drawbox=x=0:y={H-10}:w='iw*t/{max_dur:.1f}':h=10:color=cyan@0.6:t=fill",
    (
        f"drawtext=text='Canon in Dream - Venice 2023':fontfile={font_path}:"
        f"fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:"
        f"alpha='if(lt(t,1),t,if(lt(t,4),1,if(lt(t,5),1-(t-4),0)))':"
        f"shadowcolor=black:shadowx=2:shadowy=2"
    ),
    (
        f"drawtext=text='Live in Belgium\\, June 11\\, 2026!':fontfile={font_path}:"
        f"fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:"
        f"alpha='if(lt(t,40),0,if(lt(t,41),t-40,if(lt(t,43),1,if(lt(t,44),1-(t-43),0))))':"
        f"shadowcolor=black:shadowx=2:shadowy=2"
    ),
    f"fade=t=out:st={fade_start:.2f}:d=2",
]
parts.append(f"[{v_to_viz}][waves]" + ",".join(final_chain) + "[outv]")

# 8. Audio fade-out
parts.append(f"[1:a]afade=t=out:st={fade_start:.2f}:d=2[outa]")

filter_script = "/tmp/mix_filter_canon_v3.txt"
with open(filter_script, "w") as f:
    f.write(";\n".join(parts))

cmd = [
    "ffmpeg", "-y",
    "-i", KEYBOARD,
    "-i", WIDE,
    "-filter_complex_script", filter_script,
    "-map", "[outv]", "-map", "[outa]",
    "-c:v", "libx264", "-preset", "fast", "-b:v", str(bitrate),
    "-r", str(FPS), "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "320k",
    "-t", f"{max_dur:.2f}",
    OUTPUT,
]

print("\n🚀  GENERATING CANON IN DREAM V3 MIX...")
print(f"    Source duration: {max_dur:.2f}s | Fade out: {fade_start:.2f}s")
subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
print(f"\n✅  CANON IN DREAM V3 COMPLETE! Output: {OUTPUT}")
