"""v2 voice: the new lines (new.mp3) spliced with the kept phrases of the first take (vo-v1.mp3).

usage: python build_vo.py new.mp3 vo.mp3
new.mp3 holds the three new lines in order, with a pause between them:
  A  hook        "أعلى تقييم من ... والناس تشتكي من أول يوم."
  B  timeline    "ثلطعش سنة انتظار… وتأجلت مرتين، لحد الليلة."
  C  CTA         "اكتبها بالتعليقات: إي لو لا."
It is cut at its two longest pauses."""
import re, subprocess, sys
import numpy as np
SR = 48000
new, out = sys.argv[1:3]
def load(p): return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
def speech(p, d=.18):
    log = subprocess.run(["ffmpeg", "-i", p, "-af", f"silencedetect=n=-38dB:d={d}", "-f", "null", "-"], capture_output=True, text=True).stderr
    ss = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]; se = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    return list(zip(ss, se))
old, nw = load("vo-v1.mp3"), load(new)
# split the new take at its two longest inner pauses
sil = [(a, b) for a, b in speech(new) if a > .3 and b < len(nw) / SR - .3]
cuts = sorted(sorted(sil, key=lambda s: s[1] - s[0])[-2:])
if len(cuts) < 2: sys.exit("new.mp3 needs a clear pause between each of the three lines")
lead = speech(new)[0][1] if speech(new) and speech(new)[0][0] < .05 else 0
tail = len(nw) / SR
for a, b in speech(new):
    if b >= tail - .05: tail = a
A = (lead, cuts[0][0]); B = (cuts[0][1], cuts[1][0]); C = (cuts[1][1], tail)
# kept phrases of the first take (seconds in vo-v1.mp3, cut inside its pauses)
KEEP = {"question": (5.23, 7.93), "platforms": (19.51, 22.55), "score": (22.91, 25.58), "sales": (35.57, 44.06), "rest": (44.42, 70.81)}
cut = lambda x, a, b: x[int(max(a - .04, 0) * SR):int((b + .05) * SR)]
pad = lambda s: np.zeros(int(s * SR), np.float32)
parts = [cut(nw, *A), pad(.32), cut(old, *KEEP["question"]), pad(.38), cut(nw, *B), pad(.32),
         cut(old, *KEEP["platforms"]), pad(.3), cut(old, *KEEP["score"]), pad(.3), cut(old, *KEEP["sales"]), pad(.32),
         cut(old, *KEEP["rest"]), pad(.32), cut(nw, *C), pad(.4)]
x = np.concatenate(parts)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-b:a", "192k", out], input=x.tobytes(), check=True)
print(f"A {A[1]-A[0]:.2f}s  B {B[1]-B[0]:.2f}s  C {C[1]-C[0]:.2f}s  -> {out}: {len(x)/SR:.1f} s")
