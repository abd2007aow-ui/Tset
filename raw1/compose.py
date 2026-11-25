"""Overlay frames/ on cut.mp4, hold the last frame for the end card, add whooshes, master to -14 LUFS -> final.mp4"""
import json,subprocess
d=json.load(open('timeline.json'))
ts=[e['t'] for e in d['events']]+[d['total']]
total=d['total']+d['endcard']
ins=["-i","cut.mp4","-framerate","30","-i","frames/%05d.png"]
for t in ts: ins+=["-i","whoosh.wav"]
fc=[f"[0:v]tpad=stop_mode=clone:stop_duration={d['endcard']},fps=30[bg]","[bg][1:v]overlay=format=auto,format=yuv420p[v]",
    f"[0:a]apad=whole_dur={total}[voice]"]
mix=["[voice]"]
for i,t in enumerate(ts):
    ms=int(max(0,t-0.18)*1000); fc.append(f"[{i+2}:a]adelay={ms}|{ms},volume=0.35[w{i}]"); mix.append(f"[w{i}]")
fc.append("".join(mix)+f"amix=inputs={len(mix)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1:LRA=9[a]")
subprocess.run(["ffmpeg","-y","-v","error",*ins,"-filter_complex",";".join(fc),"-map","[v]","-map","[a]","-t",str(total),
  "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart","final.mp4"],check=True)
