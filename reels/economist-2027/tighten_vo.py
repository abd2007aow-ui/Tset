"""Tighten the voice: cap every pause at MAXP seconds, then speed it up a little (atempo).
usage: python tighten_vo.py vo-raw.mp3 vo.mp3 [tempo]"""
import re, subprocess, sys
import numpy as np
SR = 48000; MAXP = .28
src, out = sys.argv[1:3]; tempo = float(sys.argv[3]) if len(sys.argv) > 3 else 1.1
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
log = subprocess.run(["ffmpeg", "-i", src, "-af", "silencedetect=n=-38dB:d=0.18", "-f", "null", "-"], capture_output=True, text=True).stderr
ss = [float(v) for v in re.findall(r"silence_start: ([\d.]+)", log)]; se = [float(v) for v in re.findall(r"silence_end: ([\d.]+)", log)]
parts, t = [], 0.0
for a, b in zip(ss, se):
    if b - a > MAXP:
        keep_a = a + MAXP / 2; keep_b = b - MAXP / 2
        parts.append(x[int(t * SR):int(keep_a * SR)]); t = keep_b
parts.append(x[int(t * SR):])
y = np.concatenate(parts)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", f"atempo={tempo}", "-b:a", "192k", out], input=y.tobytes(), check=True)
print(f"{len(x)/SR:.1f} s -> {len(y)/SR/tempo:.1f} s")
