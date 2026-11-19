"""Background b-roll for the reel: gameplay shots from the official trailer (src/trailer.mp4),
cropped to 9:16, cut every ~2.5 s, as an all-keyframe VP9 webm so the page can seek it frame-exactly.
usage: python build_broll.py <seconds>   -> broll.webm
Only gameplay is used (no text cards, logos or hardware), and no women at all (the user asked for none)."""
import subprocess, sys, os
secs = float(sys.argv[1])
# (start, length, crop centre 0..1 across the 1280 px width)  - order chosen for the story
# Only shots with no women in them (checked frame by frame): cars, the street shoot-out, the store.
SHOTS = [
    (8.20, 2.0, .45),   # shoot-out on the road      (hook)
    (26.45, 2.0, .50),  # race
    (34.45, 1.4, .45),  # car on the street
    (10.30, 2.0, .62),  # shoot-out, the truck rolls
    (40.05, 1.8, .45),  # store
]
SLOW = 1.25                # play a little slower so the few shots fill the reel
CROPS = [0, .18, -.18]     # each pass moves the 9:16 window so repeats look different
W, H = 405, 720            # 9:16 window inside the 1280x720 trailer
parts, t, i = [], 0.0, 0
while t < secs:
    a, d, c = SHOTS[i % len(SHOTS)]
    if a != 3.35: c = min(max(c + CROPS[(i // len(SHOTS)) % len(CROPS)], .16), .84)
    d = min(d, (secs - t + .05) / SLOW)
    x = int(min(max(c * 1280 - W / 2, 0), 1280 - W))
    parts.append((a, d, x)); t += d * SLOW; i += 1
fc, ins = [], []
for k, (a, d, x) in enumerate(parts):
    ins += ["-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", "src/trailer.mp4"]
    fc.append(f"[{k}:v]crop={W}:{H}:{x}:0,scale=540:960,setsar=1,setpts=(PTS-STARTPTS)*{SLOW},fps=30[v{k}]")
fc.append("".join(f"[v{k}]" for k in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0,trim=0:{secs:.3f}[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[out]", "-an",
                "-c:v", "libvpx-vp9", "-g", "1", "-crf", "36", "-b:v", "0", "-deadline", "good", "-cpu-used", "4", "-row-mt", "1", "broll.webm"], check=True)
print(f"{len(parts)} shots, {secs:.1f} s -> broll.webm ({os.path.getsize('broll.webm') / 1e6:.1f} MB)")
