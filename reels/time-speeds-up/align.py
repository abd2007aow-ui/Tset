"""Align script words to a voice using pauses: words.json for Maven Reels (no Whisper)."""
import json, math, re, subprocess, sys
reel, vo, out = sys.argv[1:4]
html = open(reel, encoding="utf-8").read()
block = html.split("const SCRIPT = [")[1].split("];")[0]
lines = re.findall(r'"([^"]+)"', block)
words = [w for l in lines for w in l.split()]
lineEnd = set(); c = 0
for l in lines: c += len(l.split()); lineEnd.add(c - 1)
punct = re.compile(r'[،,.!?؟:;؛…]$')
cand = [i for i, w in enumerate(words[:-1]) if punct.search(w) or i in lineEnd]
chars = [len(re.sub(r'[^\w]', '', w)) + 1.2 for w in words]
log = subprocess.run(["ffmpeg", "-i", vo, "-af", "silencedetect=n=-38dB:d=0.18", "-f", "null", "-"], capture_output=True, text=True).stderr
ss = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
se = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
dur = float(re.search(r"Duration: (\d+):(\d+):([\d.]+)", log).group(3)) + 60 * int(re.search(r"Duration: (\d+):(\d+)", log).group(2))
start = se[0] if ss and ss[0] < .05 else 0.0
pauses = [(a, b) for a, b in zip(ss, se) if a > .05]
segs = []; t = start
for a, b in pauses: segs.append((t, a)); t = b
if dur - t > .2: segs.append((t, dur))
K, N = len(segs), len(words)
pre = [0]
for x in chars: pre.append(pre[-1] + x)
speech = sum(b - a for a, b in segs); rbar = pre[-1] / speech
ends = list(range(N)); CAND = set(cand) | {N - 1}                      # segment k ends after word ends[j]
INF = 1e18
# dp[k][j]: segments 0..k cover words 0..ends[j]
dp = [[INF] * len(ends) for _ in range(K)]; bk = [[-1] * len(ends) for _ in range(K)]
def cost(k, i0, i1):
    r = (pre[i1 + 1] - pre[i0]) / max(segs[k][1] - segs[k][0], .05)
    return math.log(r / rbar) ** 2 + (0 if i1 in CAND else .6)
for j, e in enumerate(ends): dp[0][j] = cost(0, 0, e)
for k in range(1, K):
    for j in range(len(ends)):
        for p in range(j):
            if dp[k - 1][p] < INF:
                v = dp[k - 1][p] + cost(k, ends[p] + 1, ends[j])
                if v < dp[k][j]: dp[k][j], bk[k][j] = v, p
j = len(ends) - 1; cuts = []
for k in range(K - 1, -1, -1): cuts.append(ends[j]); j = bk[k][j]
cuts = cuts[::-1]
res, rend = [], []; i0 = 0
for k, e in enumerate(cuts):
    a, b = segs[k]; tot = pre[e + 1] - pre[i0]; t = a
    for i in range(i0, e + 1):
        d = (b - a) * chars[i] / tot
        res.append([words[i], round(t, 2)]); rend.append(round(t + d, 2)); t += d
    i0 = e + 1
json.dump({"words": res, "ends": rend}, open(out, "w", encoding="utf-8"), ensure_ascii=False)
open(out.replace(".json", ".js"), "w", encoding="utf-8").write("window.VOICE = " + json.dumps({"words": res, "ends": rend}, ensure_ascii=False) + ";\n")
print(f"{K} speech segments, {N} words, rate {rbar:.1f} chars/s")
for k, e in enumerate(cuts): print(f"{segs[k][0]:6.2f}-{segs[k][1]:6.2f}  ...{' '.join(words[max(0,e-2):e+1])}")
