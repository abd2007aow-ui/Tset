"""v3 voice: new hook + the old take with some sentences cut, pauses capped, 8% faster."""
import re, subprocess, numpy as np
SR = 48000
def load(p): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout, np.float32)
def speech(p, d=.18):
    log = subprocess.run(["ffmpeg","-i",p,"-af",f"silencedetect=n=-38dB:d={d}","-f","null","-"],capture_output=True,text=True).stderr
    ss=[float(x) for x in re.findall(r"silence_start: ([\d.]+)",log)]; se=[float(x) for x in re.findall(r"silence_end: ([\d.]+)",log)]
    segs=[]; t=0.0
    for a,b in zip(ss,se):
        if a>.05: segs.append((t,a))
        t=b
    return segs, t
hook, vo = load("hook.mp3"), load("vo.mp3")
segs, _ = speech("vo.mp3")
CUT = [0.0, 4.49, 25.18, 49.74, 56.95, 57.81]   # starts of the dropped phrases
keep = [s for s in segs if not any(abs(s[0]-c) < .05 for c in CUT)]
pad = lambda s: np.zeros(int(s*SR), np.float32)
out = [hook[:int(5.44*SR)], pad(.32)]
for i,(a,b) in enumerate(keep):
    out.append(vo[int(max(a-.03,0)*SR):int((b+.04)*SR)])
    if i+1 < len(keep): out.append(pad(min(keep[i+1][0]-b, .3) if keep[i+1][0]-b > .3 else .24))
out.append(pad(.3))
x = np.concatenate(out)
subprocess.run(["ffmpeg","-v","error","-y","-f","f32le","-ar",str(SR),"-ac","1","-i","-","-af","atempo=1.08","vo3.wav"],input=x.tobytes(),check=True)
print(f"{len(keep)} kept phrases, {len(x)/SR/1.08:.1f} s")
