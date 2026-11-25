"""Original music bed made in code: warm, calm, steady (soft keys + pad + sub bass + light kick/hat).
python3 gen_music.py seconds out.wav"""
import sys, wave, numpy as np

SR = 44100
dur = float(sys.argv[1]); out = sys.argv[2]
BPM = 84; beat = 60 / BPM; bar = 4 * beat
n = int(SR * (dur + 2))
L = np.zeros(n); R = np.zeros(n)
rng = np.random.default_rng(7)

def midi(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, t0, pan=0.0, gain=1.0):
    i = int(t0 * SR); j = min(n, i + len(sig))
    if i >= n: return
    s = sig[: j - i] * gain
    L[i:j] += s * (1 - pan) / 2 * 2 ** .5 * .7071 * 2 ** .5
    R[i:j] += s * (1 + pan) / 2 * 2 ** .5 * .7071 * 2 ** .5

def keys(f, length, vel=1.0):          # soft electric-piano: few harmonics, bell attack, slow decay, tremolo
    t = np.arange(int(length * SR)) / SR
    env = np.exp(-t * 2.2) * (1 - np.exp(-t * 400))
    s = (np.sin(2*np.pi*f*t) + .35*np.sin(2*np.pi*2*f*t)*np.exp(-t*4) + .12*np.sin(2*np.pi*3.01*f*t)*np.exp(-t*7))
    return s * env * (1 + .12*np.sin(2*np.pi*4.5*t)) * vel

def pad(freqs, length):                 # slow-attack detuned sine pad
    t = np.arange(int(length * SR)) / SR
    env = np.minimum(1, t / 1.2) * np.minimum(1, (length - t) / 1.0).clip(0)
    s = sum(np.sin(2*np.pi*f*t*d) for f in freqs for d in (0.997, 1.003)) / (2*len(freqs))
    return s * env

def bass(f, length):
    t = np.arange(int(length * SR)) / SR
    env = (1 - np.exp(-t*60)) * np.exp(-t*1.1)
    return (np.sin(2*np.pi*f*t) + .25*np.sin(2*np.pi*2*f*t)) * env

def kick():
    t = np.arange(int(.35 * SR)) / SR
    f = 50 + 70*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*9)

def hat():
    t = np.arange(int(.06 * SR)) / SR
    s = rng.standard_normal(len(t)); s = np.diff(s, prepend=0)   # bright noise
    return s * np.exp(-t*80)

# Fmaj9 - Em7 - Dm9 - Cmaj7 (bright, hopeful, unobtrusive)
prog = [(53, [65, 69, 72, 76, 79]), (52, [64, 67, 71, 74]), (50, [62, 65, 69, 72, 76]), (48, [60, 64, 67, 71])]
bars = int(dur / bar) + 2
for b in range(bars):
    t0 = b * bar
    root, ch = prog[b % 4]
    add(pad([midi(m) for m in ch[:4]], bar + .6), t0, 0, .22)
    add(bass(midi(root - 12), bar), t0, 0, .42)
    # broken-chord keys: gentle 8th-note pattern
    patt = [0, 2, 1, 3, 0, 2, 4 % len(ch), 1]
    for k, idx in enumerate(patt):
        add(keys(midi(ch[idx % len(ch)]), 2.2, .9 if k % 2 == 0 else .7), t0 + k*beat/2, (-.35 if k % 2 else .35), .16)
    if b >= 1:                           # drums come in after the first bar
        for q in range(4):
            if q in (0, 2): add(kick(), t0 + q*beat, 0, .5)
            add(hat(), t0 + q*beat + beat/2, .2, .06)

mix = np.stack([L, R], 1)[: int(SR * dur)]
fade = int(SR * 2.5); mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
fi = int(SR * .8); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
mix /= np.abs(mix).max() + 1e-9; mix *= .8
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("music", out, dur, "s")
