"""Overlay frames/ on cut.mp4, add whooshes and a music bed ducked under the voice, short fade-out tail, master to -14 LUFS -> final.mp4"""
import json, subprocess
d = json.load(open('timeline.json'))
TAIL = 1.2
total = d['total'] + TAIL
ts = [e['t'] for e in d['events']]
MUSIC = None   # set to a file (e.g. a licensed track the user sends) to add a ducked music bed
ins = ["-i", "cut.mp4", "-framerate", "30", "-i", "frames/%05d.png", "-i", MUSIC or "anullsrc=r=48000:cl=stereo"]
if not MUSIC: ins[-2:-1] = ["-f", "lavfi", "-i"]
for t in ts: ins += ["-i", "whoosh.wav"]
fc = [f"[0:v]tpad=stop_mode=clone:stop_duration={TAIL},fps=30[bg]",
      f"[bg][1:v]overlay=format=auto:eof_action=repeat,fade=t=out:st={total-0.9:.3f}:d=0.9,format=yuv420p[v]",
      f"[0:a]apad=whole_dur={total},asplit=2[voice][key]",
      (f"[2:a]atrim=0:{total},volume={0.55 if MUSIC else 0},afade=t=out:st={total-2.0:.3f}:d=2.0[mus]"),
      "[mus][key]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=450:makeup=1[duck]"]
mix = ["[voice]", "[duck]"]
for i, t in enumerate(ts):
    ms = int(max(0, t - 0.18) * 1000)
    fc.append(f"[{i+3}:a]adelay={ms}|{ms},volume=0.15[w{i}]"); mix.append(f"[w{i}]")
fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1:LRA=9[a]")
subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-t", str(total),
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", "final.mp4"], check=True)
