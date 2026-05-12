#!/usr/bin/env python3
"""
mix_shorts.py
-------------
Generates a 60-second vertical (1080x1920) Shorts edit optimized for TikTok/Reels.
Features:
- Stacked Layout (Top: Keyboard, Bottom: Wide)
- Captures the 2:38 drop (Slice: 2:30 to 3:30)
- High-frequency Vibration Shake on bass hits during the drop
- Center Audio Visualizer
- Dynamic Text Overlays
"""

import subprocess, os, json
import librosa
import numpy as np

KEYBOARD = "../../01_Source_Footage/Moonlight Sonata Keyboard Shot.mov"
WIDE     = "../../01_Source_Footage/Moonlight Sonata Wide Shot.mov"
OUTPUT   = "../../02_Master_Mix/Moonlight Sonata SHORTS.mp4"

START_TIME = 150.0
DURATION = 60.0
DROP_TIME = 8.0 # 158.0 in original - 150.0 start time = 8.0 seconds in the slice

W, H = 1080, 1920
FPS = 60
BITRATE = 15000000

print("🎵 Analyzing audio slice for beat detection...")
# Load exactly the 60s slice for beat detection
y, sr = librosa.load(WIDE, sr=22050, offset=START_TIME, duration=DURATION)

# Bass detection (focusing on kicks)
S = np.abs(librosa.stft(y))
bass_energy = np.mean(S[librosa.fft_frequencies(sr=sr) < 150], axis=0)
bass_onsets = librosa.onset.onset_detect(onset_envelope=bass_energy, sr=sr, units='time')

print(f"Detected {len(bass_onsets)} Bass Hits in the slice.")

# Only vibrate on hits AFTER the drop (t > 8.0)
hits = [f"between(t\\,{o:.3f}\\,{o+0.1:.3f})" for o in bass_onsets if o > DROP_TIME]
if len(hits) > 100: hits = hits[:100]

shake_expr = "0"
if len(hits) > 0:
    shake_expr = "8*(" + "+".join(hits) + ")" # 8 pixel vibration

parts = []

# 1. Inputs (Trim to slice)
parts.append(f"[0:v]trim=start={START_TIME}:duration={DURATION},setpts=PTS-STARTPTS,fps={FPS},setsar=1[k_trim]")
parts.append(f"[1:v]trim=start={START_TIME}:duration={DURATION},setpts=PTS-STARTPTS,fps={FPS},setsar=1[w_trim]")

# 2. Scale and Crop for Stacked Layout
# Scale height to 960, keeping aspect ratio, then crop center 1080x960
parts.append(f"[k_trim]scale=-1:960,crop=1080:960[k_top]")
parts.append(f"[w_trim]scale=-1:960,crop=1080:960[w_bot]")

# 3. Stack vertically (1080x1920 total)
parts.append(f"[k_top][w_bot]vstack=inputs=2[v_stacked]")

# 4. Apply Vibration Shake (post-drop)
parts.append(f"[v_stacked]scale={W+32}:{H+32},crop={W}:{H}:(iw-ow)/2+sin(t*150)*{shake_expr}:(ih-oh)/2+cos(t*150)*{shake_expr}[v_shaken]")

# 5. Audio Split (for Visualizer and Output)
parts.append(f"[1:a]atrim=start={START_TIME}:duration={DURATION},asetpts=PTS-STARTPTS,asplit=2[a_viz][a_out_pre]")

# 6. Visualizer
parts.append(f"[a_viz]showwaves=s=1080x120:mode=line:colors=cyan@0.8:rate={FPS}[waves]")

# 7. Final Overlays and Text
font_path = "/System/Library/Fonts/Helvetica.ttc"
final_chain = [
    # Visualizer exactly in the middle (960 - half height 60)
    f"overlay=x=0:y=900:eval=frame",
    # Text 1: Title
    f"drawtext=text='Moonlight Sonata EDM Remix':fontfile={font_path}:fontsize=64:fontcolor=white:x=(w-text_w)/2:y=120:shadowcolor=black:shadowx=3:shadowy=3:alpha='if(lt(t,1),t,1)'",
    # Text 2: Wait for it...
    f"drawtext=text='Wait for the drop...':fontfile={font_path}:fontsize=56:fontcolor=yellow:x=(w-text_w)/2:y={960+120}:shadowcolor=black:shadowx=2:shadowy=2:alpha='if(lt(t,{DROP_TIME-0.5}),1,if(lt(t,{DROP_TIME}),1-2*(t-{DROP_TIME-0.5}),0))'",
    # Fade Out
    f"fade=t=out:st={DURATION-2}:d=2"
]
parts.append(f"[v_shaken][waves]" + ",".join(final_chain) + "[outv]")

# 8. Audio Fade Out
parts.append(f"[a_out_pre]afade=t=out:st={DURATION-2}:d=2[outa]")

filter_script = "/tmp/mix_filter_shorts.txt"
with open(filter_script, "w") as f: f.write(";\n".join(parts))

cmd = [
    "ffmpeg", "-y", "-i", KEYBOARD, "-i", WIDE,
    "-filter_complex_script", filter_script,
    "-map", "[outv]", "-map", "[outa]",
    "-c:v", "libx264", "-preset", "fast", "-b:v", str(BITRATE), "-r", str(FPS), "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "320k", "-t", str(DURATION), OUTPUT
]

print("\\n🚀 GENERATING VERTICAL SHORTS EDIT...")
subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
print(f"\\n✅ SHORTS EDIT COMPLETE! Output: {OUTPUT}")
