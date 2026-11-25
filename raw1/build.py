"""Edit plan for raw.mp4 -> cut.mp4 (graded, cut, gentle camera moves, 1080x1920) + events.js (overlay timeline).
python3 build.py && ffmpeg ... (see bottom)"""
import json, subprocess

SRC, START, END, PAD = "raw.mp4", 1.10, 101.55, 0.09
sil = [tuple(map(float, l.split())) for l in open("silences.txt") if l.strip()]
REMOVE = [(11.95, 15.05)]          # stutter "هسا بش قد اقدر" -> straight to "اقدر ارجع فلوس"

segs, cur = [], START
for a, b in sil:
    if b <= cur: continue
    if a > cur: segs.append([cur, a + PAD])
    cur = max(cur, b - PAD)
segs.append([cur, END])
for ra, rb in REMOVE:
    nxt = []
    for a, b in segs:
        if b <= ra or a >= rb: nxt.append([a, b]); continue
        if a < ra: nxt.append([a, ra])
        if b > rb: nxt.append([rb, b])
    segs = nxt
segs = [s for s in segs if s[1] - s[0] > 0.25]

def omap(t):
    acc = 0
    for a, b in segs:
        if t < a: return acc
        if t <= b: return acc + t - a
        acc += b - a
    return acc
total = sum(b - a for a, b in segs)

# ---- look: one grade for the whole source (so every shot matches), applied before any framing ----
GRADE = ("colorchannelmixer=rr=0.95:gg=0.985:bb=1.05,"            # neutral whites (remove the cream cast)
         "huesaturation=colors=y:saturation=-0.3:strength=1,"         # calmer wood, skin untouched
         "curves=master='0/0.035 0.25/0.235 0.5/0.49 0.75/0.735 1/0.9',"  # lifted shadows, softer highlights
         "eq=saturation=1.04")
VIGNETTE = "vignette=angle=PI/7"                                    # very soft, same on every shot

# ---- framing: two gentle sizes, each shot slowly pushes in ----
FRAMES = [dict(z=1.04, cx=360, cy=650), dict(z=1.12, cx=356, cy=625)]
PUSH = 0.012                                                         # +1.2% zoom per second
S = 3                                                                # upscale before zoompan for smooth motion
parts, labels, shots, t_out = [], [], [], 0.0
for i, (a, b) in enumerate(segs):
    f = FRAMES[i % 2]; d = b - a; nfr = max(1, round(d * 30))
    z = f"{f['z']}+{PUSH*d:.5f}*on/{nfr}"
    parts.append(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS,{GRADE},scale={720*S}:{1280*S}:flags=bicubic,"
                 f"zoompan=z='{z}':x='{f['cx']*S}-iw/zoom/2':y='{f['cy']*S}-ih/zoom/2':d=1:s=1080x1920:fps=30,{VIGNETTE},setsar=1[v{i}];")
    parts.append(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={d-0.02:.3f}:d=0.02[a{i}];")
    labels.append(f"[v{i}][a{i}]")
    shots.append(dict(t=round(t_out, 3), d=round(d, 3), z0=f["z"], dz=round(PUSH * d, 5), cx=f["cx"], cy=f["cy"]))
    t_out += d
open("cut_filter.txt", "w").write("".join(parts) + "".join(labels) + f"concat=n={len(segs)}:v=1:a=1[v][a]")

# ---------- overlay timeline (source times; mapped to output) ----------
K = lambda t, ar, en, color, **kw: dict(kind="word", t=t, ar=ar, en=en, color=color, **kw)
P = lambda t, text, icon="arrow", **kw: dict(kind="pill", t=t, text=text, icon=icon, **kw)
N = lambda t, a, b, label, tag, color, **kw: dict(kind="count", t=t, a=a, b=b, label=label, tag=tag, color=color, **kw)
C = lambda t, scene, dur, **kw: dict(kind="cut", t=t, scene=scene, dur=dur, **kw)   # full-screen illustrated cutaway
ev = [
    K(2.85, "فلـــوس", "money", "orange", dur=2.3),
    C(5.10, "clinic", 2.2, caption="المركز التجميلي"),
    K(8.30, "سوق التجميل", "beauty market", "cyan", dur=2.2, size=0.9),
    K(11.0, "اخـتلف", "it changed", "gold", dur=1.6),
    P(15.15, "أقدر أرجّع فلوسي؟", "return", dur=2.8),
    K(18.95, "السوق العراقي", "iraqi market", "white", dur=3.2, size=0.8),
    C(23.9, "price", 2.6, caption="السوق ينافس على السعر"),
    C(28.25, "laser", 3.0, caption="جهاز إزالة الشعر"),
    K(33.1, "العـائد", "return", "gold", dur=2.6),
    N(36.2, 800, 1000, "جلسة فل بدي", "قبل", "cyan", dur=3.2),
    K(40.3, "هسّا", "now", "cyan", dur=1.6),
    N(42.2, 4000, 5000, "جلسة فل بدي", "هسّا", "orange", dur=6.2),
    P(49.6, "حتى يرجّع رأس المال", "return", dur=2.8),
    K(54.3, "الرياضيات", "mathematics", "white", dur=2.8),
    dict(kind="chips", t=60.8, items=["الأيام", "الأسابيع", "الأشهر", "سعر الجلسة"], gaps=[0, 1.9, 2.4, 3.1], dur=4.2),
    K(67.4, "متشائم؟", "pessimistic?", "white", dur=0.95, size=0.8),
    K(68.3, "بالعـكس", "on the contrary", "gold", dur=2.0),
    dict(kind="versus", t=72.8, left="مستعمل", right="جديد", note="أقل سعراً", dur=3.4),
    P(79.0, "صيانة", "wrench", dur=1.9),
    K(81.4, "الاستقرار", "stability", "cyan", dur=1.9, size=0.85),
    K(83.2, "الجدوى الاقتصادية", "feasibility", "gold", dur=4.0, size=0.72),
    P(90.3, "احسبها قبل الشراء", "calc", dur=3.4),
    C(96.2, "price", 2.4, caption="نزول في أسعار الجلسات"),
    K(98.5, "احـسب", "do the math", "gold", dur=2.6),
]
cuts = [s["t"] for s in shots[1:]]
for e in ev:
    e["t"] = round(omap(e["t"]), 3)
    if e["kind"] == "cut":                 # start a cutaway exactly on a nearby cut so it also hides that jump
        near = min(cuts, key=lambda c: abs(c - e["t"]))
        if abs(near - e["t"]) < 0.7: e["t"] = round(near, 3)
TL = dict(total=round(total, 3), endcard=0, events=ev, cuts=cuts, shots=shots,
          label=dict(x0=238, y0=252, x1=492, y1=322))     # old burned-in label, source pixels (with margin)
json.dump(TL, open("timeline.json", "w"), ensure_ascii=False, indent=1)
open("events.js", "w").write("window.TL=" + json.dumps(TL, ensure_ascii=False) + ";")
print(f"{len(segs)} shots, output {total:.1f}s, avg shot {total/len(segs):.2f}s")
