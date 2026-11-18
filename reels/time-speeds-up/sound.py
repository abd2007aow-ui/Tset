#!/usr/bin/env python3
"""Sound for the reel, made in code: an original music bed + a sound effect on every cue, ducked under the voice.

usage: python sound.py out.cues.json vo.mp3 bed.wav [--seconds 74.4]
Then:  node render.mjs reel.html out.mp4 --voice vo.mp3 --music bed.wav --music-db 0
"""
import argparse, json, subprocess
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def db(x): return 10 ** (x / 20)
def env(n, a, r): # attack/release envelope in samples
    e = np.ones(n); a = min(a, n); e[:a] = np.linspace(0, 1, a); e[n - min(r, n):] *= np.linspace(1, 0, min(r, n)); return e
def lp_fast(x, fc):   # one-pole lowpass applied in the frequency domain (fast for long signals)
    a = np.exp(-2 * np.pi * fc / SR); n = len(x); N = 1 << int(np.ceil(np.log2(n + SR)))
    w = 2 * np.pi * np.fft.rfftfreq(N)
    return np.fft.irfft(np.fft.rfft(x, N) * (1 - a) / (1 - a * np.exp(-1j * w)), N)[:n]
def reverb(x, secs=2.2, wet=.28):
    n = int(SR * secs); ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 7, n)); ir = lp_fast(ir, 5000); ir /= np.sqrt((ir ** 2).sum())
    N = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[:len(x)]
    return x * (1 - wet) + y * wet * 3
def hz(midi): return 440 * 2 ** ((midi - 69) / 12)


# ---------------- sound effects ----------------
def sfx_pop(i):
    n = int(.09 * SR); t = np.arange(n) / SR; f0 = 900 + 180 * (i % 5)
    f = f0 * np.exp(-t * 14); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 45) * .55
def sfx_whoosh():
    n = int(.42 * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    sweep = lp_fast(noise, 2500) - lp_fast(noise, 300)
    shape = np.sin(np.pi * (t / t[-1]) ** .7) ** 2
    return sweep * shape * .9
def sfx_hit():
    n = int(.9 * SR); t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(55 + 90 * np.exp(-t * 18)) / SR) * np.exp(-t * 5.5)
    click = lp_fast(rng.standard_normal(n), 3000) * np.exp(-t * 60) * .8
    return (boom * 1.1 + click) * .9
def sfx_tick():
    n = int(.05 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 3200 * t) + .6 * np.sin(2 * np.pi * 5100 * t)) * np.exp(-t * 160) * .35
def sfx_land():
    n = int(.35 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(140 * np.exp(-t * 9)) / SR) * np.exp(-t * 14) * .9


# ---------------- music: calm, reflective, a clock under it ----------------
def music(seconds, voice_on):
    n = int(seconds * SR); out = np.zeros(n)
    bpm = 76; beat = 60 / bpm; bar = beat * 4
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]       # Am F C G
    pad = np.zeros(n); keys = np.zeros(n); bass = np.zeros(n); tick = np.zeros(n)
    nb = int(np.ceil(seconds / bar))
    for b in range(nb):
        ch = chords[b % 4]; s0 = int(b * bar * SR); L = int(bar * SR) + int(.6 * SR)
        t = np.arange(L) / SR
        e = env(L, int(.7 * SR), int(1.0 * SR))
        for m in ch:
            for det in (-.07, .07):
                f = hz(m + 12 * 0) * (1 + det / 100)
                pad_seg = (np.sin(2 * np.pi * f * t) + .3 * np.sin(4 * np.pi * f * t)) * e * .1
                seg = pad[s0:s0 + L]; seg += pad_seg[:len(seg)]
        f = hz(ch[0] - 24); bl = int(bar * SR)
        bseg = np.sin(2 * np.pi * f * t[:bl]) * env(bl, 2000, int(.4 * SR)) * .22
        seg = bass[s0:s0 + bl]; seg += bseg[:len(seg)]
        # soft piano arpeggio, eighth notes
        arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 24, ch[2] + 12, ch[1] + 12, ch[0] + 24, ch[2] + 12]
        for k, m in enumerate(arp):
            s = s0 + int(k * beat / 2 * SR); L2 = int(1.4 * SR); tt = np.arange(L2) / SR; f = hz(m)
            note = (np.sin(2 * np.pi * f * tt) + .45 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 3) + .2 * np.sin(6 * np.pi * f * tt) * np.exp(-tt * 6))
            note *= np.exp(-tt * 3.2) * (1 - np.exp(-tt * 400)) * (.16 if k % 2 == 0 else .11)
            seg = keys[s:s + L2]; seg += note[:len(seg)]
        for k in range(4):   # the clock
            s = s0 + int(k * beat * SR); c = sfx_tick() * (.5 if k % 2 == 0 else .32)
            seg = tick[s:s + len(c)]; seg += c[:len(seg)]
    T = np.arange(n) / SR
    # arrangement over the story: hook / childhood / adult routine / meaning / ending
    keys_lvl = np.interp(T, [0, 4, 5, 34, 36, 56, 58, 65, 67, seconds], [.0, .0, 1, 1, .55, .55, .8, .8, 1.2, 1.2])
    tick_lvl = np.interp(T, [0, 34, 35, 49, 50, 56, 58, seconds], [1, 1, 1.6, 1.6, .7, .7, .4, .4])
    pad_lvl = np.interp(T, [0, 1.5, 56, 58, 65, 67, seconds], [.5, 1, 1, 1.25, 1.25, 1.4, 1.4])
    out = pad * pad_lvl + keys * keys_lvl + bass + tick * tick_lvl
    out = reverb(lp_fast(out, 6000), 2.4, .3)
    out *= env(n, int(.8 * SR), int(2.2 * SR))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cues"); ap.add_argument("voice"); ap.add_argument("out")
    ap.add_argument("--seconds", type=float, default=None); ap.add_argument("--music-db", type=float, default=-19)
    ap.add_argument("--sfx-db", type=float, default=-9)
    a = ap.parse_args()
    v = load(a.voice); cues = json.load(open(a.cues))
    seconds = a.seconds or max(len(v) / SR + 2.5, cues[-1]["t"] + 1.5)
    n = int(seconds * SR); v = np.pad(v, (0, max(0, n - len(v))))[:n]
    vrms = np.sqrt(np.mean(v[np.abs(v) > db(-45)] ** 2))
    # ducking: music dips while the voice talks
    e = np.abs(v); e = lp_fast(e, 6); e = e / (e.max() + 1e-9)
    on = np.clip(e / .12, 0, 1); duck = 1 - .45 * lp_fast(on, 2)
    m = music(seconds, on); m *= vrms * db(a.music_db) / np.sqrt(np.mean(m ** 2) + 1e-12); m *= duck
    # sound effects, thinned so they never pile up
    fx = np.zeros(n); last = {}; pops = 0
    for c in cues:
        k, t = c["kind"], c["t"]
        if t - last.get(k, -9) < (.09 if k == "pop" else .25): continue
        last[k] = t
        if k == "pop": s, g = sfx_pop(pops), .55; pops += 1
        elif k == "whoosh": s, g = sfx_whoosh(), .7
        elif k == "hit": s, g = sfx_hit(), .5
        elif k == "tick": s, g = sfx_tick(), .6
        else: s, g = sfx_land(), .8
        i = int(max(t - (.18 if k == "whoosh" else 0), 0) * SR); seg = fx[i:i + len(s)]; seg += s[:len(seg)] * g
    fx = reverb(fx, .9, .18)
    fx *= vrms * db(a.sfx_db) / (np.sqrt(np.mean(fx[np.abs(fx) > 1e-4] ** 2)) + 1e-12)
    bed = m + fx
    peak = np.abs(bed).max()
    if peak > .95: bed *= .95 / peak
    pcm = (np.clip(bed, -1, 1) * 32767).astype("<i2").tobytes()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", a.out], input=pcm, check=True)
    print(f"wrote {a.out}: {seconds:.1f} s, music {a.music_db} dB and effects {a.sfx_db} dB under the voice")


if __name__ == "__main__":
    main()
