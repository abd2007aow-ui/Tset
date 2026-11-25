"""Edit plan for raw.mp4: cut silences, alternate wide/close, grade, and write the overlay timeline.
python3 build.py  -> writes cut.mp4 (graded, cut, 1080x1920) and events.js (overlay timeline in output seconds)"""
import json, subprocess

SRC, START, END, PAD = "raw.mp4", 1.10, 101.55, 0.10
sil = [tuple(map(float, l.split())) for l in open("silences.txt") if l.strip()]

# speech runs between silences
segs, cur = [], START
for a, b in sil:
    if b <= cur: continue
    if a > cur: segs.append([cur, a + PAD])
    cur = max(cur, b - PAD)
segs.append([cur, END])
segs = [s for s in segs if s[1] - s[0] > 0.25]

# split runs longer than 5.5 s so a shot change still comes every few seconds
out = []
for a, b in segs:
    n = max(1, round((b - a) / 4.5))
    for i in range(n): out.append([a + (b - a) * i / n, a + (b - a) * (i + 1) / n])
segs = out

# map source time -> output time
def omap(t):
    acc = 0
    for a, b in segs:
        if t < a: return acc
        if t <= b: return acc + t - a
        acc += b - a
    return acc
total = sum(b - a for a, b in segs)

# shots: wide / close alternate; close is a 1.5x crop on the face
W, H = 720, 1280
CLOSE = dict(w=480, h=854, x=110, y=150)
WIDE = dict(w=684, h=1216, x=18, y=40)
GRADE = ("eq=contrast=1.10:brightness=-0.07:saturation=0.80:gamma=0.95,"
         "colorbalance=rs=-0.10:gs=-0.02:bs=0.12:rm=-0.05:gm=0.0:bm=0.05:rh=0.03:gh=0.01:bh=-0.03,"
         "vignette=angle=PI/4.2")
# hide the old burned-in label above the head
DELOGO = "delogo=x=238:y=252:w=232:h=56"

parts, labels = [], []
for i, (a, b) in enumerate(segs):
    c = CLOSE if i % 2 else WIDE
    parts.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS,{DELOGO},crop={c['w']}:{c['h']}:{c['x']}:{c['y']},"
                 f"scale=1080:1920:flags=lanczos,setsar=1,{GRADE}[v{i}];")
    parts.append(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={b-a-0.02:.3f}:d=0.02[a{i}];")
    labels.append(f"[v{i}][a{i}]")
fc = "".join(parts) + "".join(labels) + f"concat=n={len(segs)}:v=1:a=1[v][a]"
open("cut_filter.txt", "w").write(fc)

# ---------- overlay timeline (source times; mapped to output) ----------
K = lambda t, ar, en, color, **kw: dict(kind="word", t=t, ar=ar, en=en, color=color, **kw)
P = lambda t, text, icon="arrow", **kw: dict(kind="pill", t=t, text=text, icon=icon, **kw)
N = lambda t, a, b, label, tag, color, **kw: dict(kind="count", t=t, a=a, b=b, label=label, tag=tag, color=color, **kw)
ev = [
    K(2.85, "فلـــوس", "money", "orange", dur=3.6),
    P(4.30, "جهاز للمركز التجميلي", "device", dur=2.8),
    K(8.30, "سوق التجميل", "beauty market", "cyan", dur=2.2),
    K(11.0, "اخـتلف", "it changed", "gold", dur=2.6),
    P(15.15, "أقدر أرجّع فلوسي؟", "return", dur=3.0),
    K(18.95, "السوق العراقي", "iraqi market", "white", dur=3.6, size=0.8),
    K(24.0, "السعـر", "price", "orange", dur=3.0),
    P(28.3, "جهاز إزالة شعر", "laser", dur=3.6),
    K(33.1, "العـائد", "return", "gold", dur=3.0),
    N(36.2, 800, 1000, "جلسة فل بدي", "قبل", "cyan", dur=3.4),
    K(40.3, "هسّـا", "now", "cyan", dur=1.8),
    N(42.2, 4000, 5000, "جلسة فل بدي", "هسّا", "orange", dur=6.4),
    P(49.6, "حتى يرجّع رأس المال", "return", dur=3.0),
    K(54.3, "الرياضيات", "mathematics", "white", dur=3.0),
    dict(kind="chips", t=60.8, items=["الأيام", "الأسابيع", "الأشهر", "سعر الجلسة"], gaps=[0, 1.9, 2.4, 3.1], dur=4.2),
    K(67.4, "متشائم؟", "pessimistic?", "white", dur=1.0, size=0.8),
    K(68.3, "بالعـكس", "on the contrary", "gold", dur=2.2),
    dict(kind="versus", t=72.8, left="مستعمل", right="جديد", note="أقل سعراً", dur=3.6),
    P(79.0, "صيانة", "wrench", dur=2.0),
    K(81.4, "الاستقرار", "stability", "cyan", dur=2.0, size=0.85),
    K(83.2, "الجدوى الاقتصادية", "feasibility", "gold", dur=4.2, size=0.72),
    P(90.3, "احسبها قبل الشراء", "calc", dur=3.6),
    dict(kind="down", t=96.3, ar="نزول", en="session prices", dur=2.0),
    K(98.5, "احـسب", "do the math", "gold", dur=3.0),
]
for e in ev:
    e["t"] = round(omap(e["t"]), 3)
END_CARD = 2.6
cuts = [round(omap(a) + 0.001, 3) for a, _ in segs[1:]]
json.dump(dict(total=round(total, 3), endcard=END_CARD, events=ev, cuts=cuts), open("timeline.json", "w"), ensure_ascii=False, indent=1)
open("events.js", "w").write("window.TL=" + json.dumps(dict(total=round(total, 3), endcard=END_CARD, events=ev, cuts=cuts), ensure_ascii=False) + ";")
print(f"{len(segs)} shots, output {total:.1f}s (+{END_CARD}s end card), avg shot {total/len(segs):.2f}s")
