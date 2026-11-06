"""想一想樂園 (Think-Think Park): every sound in the app, made here from sine
waves and noise, so every one is ours: nothing recorded, nothing downloaded,
and every tune written for this app.

- Music (WAV, 16,000 Hz): a tune for the park map, one for each land, and a
  lullaby for rest time. Each has its own metre, key and instruments, so a
  child can hear where they are:
  - music_park: a gentle merry-go-round waltz (3/4, D) on a band organ's
    flute pipes, oom-pah-pah, a glockenspiel in the second half.
  - music_city (卡通城): a bouncy cartoon tune (4/4, B flat): pizzicato
    strings, ukulele chops, a plucked bass, light percussion, a slide whistle.
  - music_forest (紙片森林): warm and cosy (6/8, E): a kalimba, then a little
    wooden flute, over a fingerpicked nylon guitar.
  - music_blocks (積木王國): tidy patterns (4/4, C): a xylophone, a marimba
    bass in 3+3+2, little glassy plinks, wooden blocks.
  - music_rest: a slow lullaby (6/8, E flat): a music box over a felt piano.
  Each tune is as long as its bars, and what still rings at the end is
  carried round to the start, so it loops without a seam.
- Short sounds, 阿布's voice and the thank-you voices of everyone who gets
  their things back (WAV, 22,050 Hz).
- For children from 2 and a half: fun, warm and soft. Nothing harsh or
  sudden; a wrong try is a friendly "uh-oh", never a buzzer.
- Voices are a buzz through formant filters, as in the sibling apps.
- Every random choice uses a fixed seed, so each run writes the same files.
- Every short sound is set to the same loudness as heard through a phone
  speaker (A-weighting, and nothing under 250 Hz), plus or minus a few dB
  where it should sit softer, with its peak at most 0.72. The music is set
  the same way, about 8 dB under the short sounds. Low sounds get a little
  of their own overtones added (`carry`), so a phone still carries them.

The helpers (t_of, env, sweep, decay, lowpass, bandpass, highpass, norm,
partial, bell, marimba, place, tune_loop, resonator, voice, ease, glide,
bubble, above, spans, melody, root_of, third_of, kalimba, pluck_bass, metal,
woodblock, shaker, noise_through, music_box_note, soft_piano, triangle,
carry, round_off, celesta, chime, a_weight, loudness, tidy, level, write,
report, read, preview) come from 小卡認天下's design/sounds/make_sounds.py;
uke, kick and jingle from 動物小餐廳's, xylo from 字母寵物's. The dog, cat,
cow, sheep, hen, bird, monkey and frog, and Für Elise (Beethoven, 1810: the
garbage truck's tune), are adapted from 小卡認天下 (which took them from
畫畫小鎮); the bee from 畫畫小鎮's buzz. The instruments calliope,
organ_bass, pizz, guitar, flute, plink, clack, slide_whistle and toy_horn,
phone_ready (silence around the 70 Hz filter, so its ring stays out of the
sound), the seam check, and every tune and other sound, are new.

    python3 design/sounds/make_sounds.py                  # writes app/assets/sounds/*.wav
    python3 design/sounds/make_sounds.py preview OUT.m4a  # and a listening preview
"""
import pathlib
import subprocess
import sys
import wave

import numpy as np
from scipy.signal import lfilter, resample_poly

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "app" / "assets" / "sounds"
SR = 22050       # short sounds and voices
LOOP_SR = 16000  # music
LIMIT = 4_500_000  # bytes, the whole folder

# Notes (Hz), with flats as well as sharps.
NOTE = {f"{n}{o}": 440 * 2 ** ((k - 9) / 12 + o - 4)
        for o in range(1, 9) for k, n in enumerate("C C# D D# E F F# G G# A A# B".split())}
for _o in range(1, 9):
    for _flat, _sharp in (("Db", "C#"), ("Eb", "D#"), ("Gb", "F#"), ("Ab", "G#"), ("Bb", "A#")):
        NOTE[f"{_flat}{_o}"] = NOTE[f"{_sharp}{_o}"]


# ---------------------------------------------------------------- helpers (from 小卡認天下, 動物小餐廳 and 字母寵物)


def t_of(dur, sr=SR):
    return np.arange(int(dur * sr)) / sr


def env(n, attack=0.005, release=0.05, sr=SR):
    """Up quickly, down smoothly: no clicks at either end."""
    e = np.ones(n)
    a, r = max(1, min(n, int(attack * sr))), max(1, min(n, int(release * sr)))
    e[:a] = np.linspace(0, 1, a) ** 2
    e[-r:] *= np.linspace(1, 0, r) ** 2
    return e


def sweep(f, sr=SR):
    """A sine whose frequency follows the array [f] (Hz per sample)."""
    return np.sin(2 * np.pi * np.cumsum(f) / sr)


def decay(n, tau, sr=SR):
    return np.exp(-np.arange(n) / (tau * sr))


def lowpass(x, cutoff, sr=SR):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (freqs / cutoff) ** 4)
    return np.fft.irfft(spec, len(x))


def bandpass(x, lo, hi, sr=SR):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (lo / np.maximum(freqs, 1)) ** 4) / (1 + (freqs / hi) ** 4)
    return np.fft.irfft(spec, len(x))


def highpass(x, cutoff, sr=SR):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (cutoff / np.maximum(freqs, 1e-3)) ** 4)
    return np.fft.irfft(spec, len(x))


def norm(x):
    return x / max(1e-9, np.abs(x).max())


def partial(freq, t, sr):
    """A sine at [freq], or silence if it is too high for [sr] (it would fold
    back down as a wrong note)."""
    return np.sin(2 * np.pi * freq * t) if freq < 0.45 * sr else np.zeros_like(t)


def bell(freq, dur=0.5, sr=SR, bright=1.0):
    """A soft glockenspiel note: a few partials, the high ones dying first."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.35))
         + 0.35 * bright * partial(freq * 2.76, t, sr) * np.exp(-t / (dur * 0.12))
         + 0.15 * bright * partial(freq * 5.4, t, sr) * np.exp(-t / (dur * 0.06)))
    return x * env(len(t), 0.002, 0.03, sr)


def marimba(freq, dur=0.5, sr=SR):
    t = t_of(dur, sr)
    x = partial(freq, t, sr) * np.exp(-t / (dur * 0.3)) + 0.2 * partial(freq * 4, t, sr) * np.exp(-t / (dur * 0.05))
    return x * env(len(t), 0.003, 0.03, sr)


def xylo(freq, dur=0.5, sr=LOOP_SR):
    """A wooden xylophone bar: the marimba's knock with a little ring on top."""
    wood = 0.8 * marimba(freq, dur, sr)
    ring = 0.15 * bell(freq, dur * 0.8, sr, bright=0.3)
    wood[:len(ring)] += ring
    return wood


def place(total, parts, sr=SR):
    """[parts]: (start seconds, signal) mixed into [total] seconds."""
    out = np.zeros(int(total * sr))
    for start, sig in parts:
        i = int(start * sr)
        j = min(len(out), i + len(sig))
        out[i:j] += sig[: j - i]
    return out


def tune_loop(seconds, notes, sr=LOOP_SR):
    """[notes]: (start seconds, signal); what rings past [seconds] wraps to the start."""
    n = int(round(seconds * sr))
    tail = max(len(sig) + int(start * sr) for start, sig in notes) - n
    out = np.zeros(n + max(0, tail))
    for start, sig in notes:
        i = int(start * sr)
        out[i:i + len(sig)] += sig
    loop = out[:n].copy()
    if tail > 0:
        loop[:tail] += out[n:]
    return loop


def resonator(x, freq, bw, sr=SR, block=64):
    """A two-pole resonance at [freq] Hz (a number, or one per sample, for a
    sound that changes) of bandwidth [bw] Hz."""
    freq = np.broadcast_to(np.asarray(freq, dtype=float), x.shape)
    y, zi = np.zeros_like(x), np.zeros(2)
    r = np.exp(-np.pi * bw / sr)
    for i in range(0, len(x), block):
        th = 2 * np.pi * freq[i] / sr
        y[i:i + block], zi = lfilter([1 - r], [1, -2 * r * np.cos(th), r * r], x[i:i + block], zi=zi)
    return y


def voice(f0, formants, rng, breath=0.03, rough=0.0, sr=SR):
    """A voice at pitch [f0] (Hz per sample) through [formants]: (Hz or Hz
    per sample, bandwidth, gain). [rough] jitters the pitch, for a growl."""
    n = len(f0)
    if rough:
        f0 = f0 * (1 + rough * lowpass(rng.standard_normal(n), 60, sr) * 3)
    buzz = 2 * (np.cumsum(f0) / sr % 1) - 1 + breath * rng.standard_normal(n)
    out = np.zeros(n)
    for f, bw, gain in formants:
        y = resonator(buzz, f, bw, sr)
        out += gain * y / max(1e-9, np.abs(y).max())
    return lowpass(out, 3800, sr)  # soft, not a kazoo


def ease(u):
    """0 to 1, smoothly, over u in 0..1."""
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def glide(t, *points):
    """A value that moves smoothly between (time, value) [points]."""
    ts, vs = zip(*points)
    out = np.interp(t, ts, vs)
    return lowpass(out - out.mean(), 25) + out.mean() if len(t) > 64 else out


def bubble(rng, sr=SR, low=(300, 550), rise=(2.2, 3.2), dur=(0.04, 0.08)):
    """One little bubble: a quick rising blip that starts and ends at zero."""
    d = rng.uniform(*dur)
    t = t_of(d, sr)
    f0 = rng.uniform(*low)
    f = np.geomspace(f0, f0 * rng.uniform(*rise), len(t))
    return sweep(f, sr) * np.sin(np.pi * t / d)


def above(name, low):
    """The note called [name] (no octave) at or just above the note [low]."""
    for o in range(1, 9):
        if NOTE[f"{name}{o}"] >= NOTE[low] * 0.999:
            return f"{name}{o}"
    raise ValueError(name)


def spans(bars, beats_per_bar):
    """Bars like "F" or "Gm-C" (two chords, half a bar each) -> (beat, length in beats, chord)."""
    out = []
    for i, bar in enumerate(bars):
        parts = bar.split("-")
        each = beats_per_bar / len(parts)
        out += [(i * beats_per_bar + k * each, each, c) for k, c in enumerate(parts)]
    return out


def melody(tune, beat, start=0.0, swing=0.0, bars=None, beats_per_bar=4):
    """[tune]: (note or None for a rest, beats) one after another ->
    (seconds, note, seconds long). [swing] (in beats) delays each note that
    falls halfway through a beat, for a lilt. [bars]: check the tune fills them."""
    if bars is not None:
        assert abs(sum(b for _, b in tune) - bars * beats_per_bar) < 1e-9, tune
    out, b = [], 0.0
    for name, beats in tune:
        if name:
            late = swing if abs(b % 1 - 0.5) < 1e-6 else 0.0
            out.append((start + (b + late) * beat, name, (beats - late) * beat))
        b += beats
    return out


def root_of(chord):
    return chord[:2] if len(chord) > 1 and chord[1] in "#b" else chord[0]


def third_of(chord):
    """Semitones from the root to the third: 3 for a minor chord, else 4."""
    rest = chord[len(root_of(chord)):]
    return 3 if rest.startswith("m") and not rest.startswith("maj") else 4


def kalimba(freq, dur=1.8, sr=LOOP_SR):
    """A thumb piano's tine: a round note and a quick metal tick high above it
    (a tine's second mode is about 6.3 times the first)."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.3))
         + 0.28 * partial(freq * 6.27, t, sr) * np.exp(-t / 0.025)
         + 0.08 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.08)))
    return x * env(len(t), 0.001, 0.08, sr)


def pluck_bass(freq, dur=1.0, sr=LOOP_SR):
    """A plucked double bass: round, short, warm."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.35))
         + 0.45 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.15))
         + 0.15 * partial(freq * 3, t, sr) * np.exp(-t / (dur * 0.08)))
    return x * env(len(t), 0.006, 0.08, sr)


def uke(freq, dur=1.0, sr=LOOP_SR, bright=1.0, pos=0.18):
    """A ukulele's nylon string: whole-number harmonics shaped by where it is
    plucked ([pos] along the string), the high ones fading first."""
    t = t_of(dur, sr)
    x = np.zeros_like(t)
    for k in range(1, 10):
        a = abs(np.sin(np.pi * k * pos)) / np.sin(np.pi * pos) / k ** 1.5
        x += (a if k == 1 else a * bright) * partial(freq * k, t, sr) * np.exp(-t / (dur * 0.3 / (1 + 0.5 * (k - 1))))
    return x * env(len(t), 0.002, 0.05, sr)


def metal(freq, dur, sr=SR, ratios=(1, 1.59, 2.14, 2.65, 3.15), amps=(1, .6, .45, .3, .2), taus=(.5, .3, .2, .15, .1)):
    """A small metal ting (a bell, a coin): partials that are not
    whole-number multiples; [taus] are fractions of [dur]."""
    t = t_of(dur, sr)
    x = sum(a * partial(freq * r, t, sr) * np.exp(-t / (dur * k)) for r, a, k in zip(ratios, amps, taus))
    return x * env(len(t), 0.0008, 0.03, sr)


def woodblock(freq, sr=LOOP_SR, dur=0.09):
    t = t_of(dur, sr)
    x = partial(freq, t, sr) * np.exp(-t / 0.018) + 0.45 * partial(freq * 2.3, t, sr) * np.exp(-t / 0.007)
    return x * env(len(t), 0.0008, 0.02, sr)


def shaker(rng, sr=LOOP_SR, dur=0.06):
    n = int(dur * sr)
    return norm(bandpass(rng.standard_normal(n), 3000, 7000, sr)) * env(n, 0.006, dur * 0.8, sr)


def kick(sr=LOOP_SR, dur=0.16):
    n = int(dur * sr)
    return sweep(np.geomspace(130, 55, n), sr) * decay(n, 0.05, sr) * env(n, 0.002, 0.04, sr)


def jingle(rng, dur=0.2, sr=SR):
    """A tambourine's little cymbals."""
    t = t_of(dur, sr)
    x = sum(rng.uniform(0.4, 1.0) * partial(f, t, sr) * np.exp(-t / rng.uniform(0.03, 0.07))
            for f in rng.uniform(4500, 9000, 8))
    x += 0.5 * norm(bandpass(rng.standard_normal(len(t)), 5000, 10000, sr)) * np.exp(-t / 0.02)
    return x * env(len(t), 0.001, 0.04, sr)


def noise_through(rng, centre, bw, n, sr=SR):
    """Noise through a resonance that can move: the voice of air and water."""
    return norm(resonator(rng.standard_normal(n), centre, bw, sr))


def music_box_note(freq, dur, sr=LOOP_SR, bright=1.0):
    """A music box's comb: bright at first, then a long soft ring."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / 0.9)
         + 0.4 * bright * partial(freq * 3.0, t, sr) * np.exp(-t / 0.18)
         + 0.18 * bright * partial(freq * 5.2, t, sr) * np.exp(-t / 0.06))
    return x * env(len(t), 0.002, 0.08, sr)


def soft_piano(freq, dur=2.5, sr=LOOP_SR):
    """A felt piano: a marimba's warm knock and a bell's soft ring, blended,
    over a plain tone that rings a little longer."""
    t = t_of(dur, sr)
    body = (partial(freq, t, sr) * np.exp(-t / (dur * 0.32))
            + 0.25 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.12)))
    x = 0.45 * marimba(freq, dur, sr) + 0.3 * bell(freq, dur, sr, bright=0.25) + 0.5 * body
    return x * env(len(t), 0.006, 0.08, sr)


def triangle(freq, dur, sr=SR):
    t = t_of(dur, sr)
    return 2 / np.pi * np.arcsin(np.sin(2 * np.pi * freq * t))


def carry(x, amount=0.3, lo=500, hi=3000, drive=2.5, sr=SR):
    """Phone speakers hardly play anything under about 300 Hz. For a low
    sound, add its own overtones (a soft saturation of it, kept to [lo]..[hi]
    Hz): a phone plays those, and the ear still hears the low note."""
    peak = max(1e-9, np.abs(x).max())
    over = bandpass(np.tanh(drive * x / peak), lo, hi, sr)
    return x + amount * peak * norm(over)


def round_off(x, drive=2.0):
    """Round off the tallest peaks (a soft saturation), so a sound made of
    quick hits can be as loud as the others without going over the peak."""
    return np.tanh(drive * norm(x)) / np.tanh(drive)


def celesta(freq, dur=1.0, sr=LOOP_SR):
    """A celesta: a felt hammer on a small steel bar over a wooden box. A
    sweet, round tone with a little of its octave, and a soft tick."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.3))
         + 0.25 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.12))
         + 0.06 * partial(freq * 4.1, t, sr) * np.exp(-t / 0.02))
    return x * env(len(t), 0.0015, 0.05, sr)


def chime(freq, dur, sr=SR):
    """A soft, warm bell: whole-number partials (no glockenspiel clang), two
    tones a hair apart so it shimmers as it rings."""
    t = t_of(dur, sr)
    x = ((partial(freq, t, sr) + 0.5 * partial(freq * 1.003, t, sr)) * np.exp(-t / (dur * 0.38))
         + 0.28 * partial(freq * 2.0, t, sr) * np.exp(-t / (dur * 0.16))
         + 0.1 * partial(freq * 3.01, t, sr) * np.exp(-t / (dur * 0.07)))
    return x * env(len(t), 0.003, 0.08, sr)


def a_weight(x, sr):
    """[x] as the ear hears it out of a phone: A-weighting (the ear is less
    sensitive to low and very high sounds) and nothing under about 250 Hz."""
    spec = np.fft.rfft(x)
    f2 = np.fft.rfftfreq(len(x), 1 / sr) ** 2
    ra = 12194 ** 2 * f2 ** 2 / ((f2 + 20.6 ** 2) * np.sqrt((f2 + 107.7 ** 2) * (f2 + 737.9 ** 2)) * (f2 + 12194 ** 2))
    phone = 1 / (1 + (250 ** 2 / np.maximum(f2, 1e-6)) ** 2)
    return np.fft.irfft(spec * ra * 1.2589 * phone, len(x))


def loudness(x, sr):
    """How loud [x] sounds, roughly, in dB: the weighted power in 200 ms
    windows (the ear adds up about that long, so a click sounds softer than
    a note as loud), over the windows within 20 dB of the loudest one."""
    y = a_weight(np.asarray(x, dtype=np.float64), sr) ** 2
    w, hop = int(0.2 * sr), int(0.025 * sr)
    y = np.concatenate([y, np.zeros(max(0, w - len(y)))])
    c = np.concatenate([[0], np.cumsum(y)])
    e = (c[w::hop] - c[:len(c) - w:hop]) / w
    return 10 * np.log10(max(1e-12, np.mean(e[e >= e.max() * 0.01])))


# ---------------------------------------------------------------- new helpers

QUALITY = {"": (0, 4, 7), "m": (0, 3, 7), "7": (0, 4, 7, 10), "m7": (0, 3, 7, 10)}
C_MAJOR = "C D E F G A B".split()


def chord_tones(chord, low):
    """The notes (Hz) of [chord], root first, the root at or just above [low]."""
    root = root_of(chord)
    f = NOTE[above(root, low)]
    return [f * 2 ** (s / 12) for s in QUALITY[chord[len(root):]]]


def third_below(name):
    """The note a third below [name] in C major (for a second voice)."""
    letter, octave = name[:-1], int(name[-1])
    i = C_MAJOR.index(letter) - 2
    return f"{C_MAJOR[i % 7]}{octave - (1 if i < 0 else 0)}"


def harmonics(f, sr=SR, tilt=1.0):
    """A bright tone at pitch [f] (Hz per sample) with every harmonic up to
    near half the sample rate, each 1/k^[tilt]: a sawtooth without the
    harsh folded-back tones."""
    ph = 2 * np.pi * np.cumsum(f) / sr
    top = int(0.45 * sr // np.max(f))
    return sum(np.sin(k * ph) / k ** tilt for k in range(1, max(2, top + 1)))


def calliope(freq, dur, rng, sr=LOOP_SR):
    """A band organ's flute pipe, as on a merry-go-round: a round tone with a
    little of its octave and twelfth, a soft chiff of air as it speaks, and
    the gentle flutter of the organ's wind."""
    t = t_of(dur, sr)
    n = len(t)
    flutter = np.sin(2 * np.pi * 6.2 * t)
    ph = 2 * np.pi * np.cumsum(freq * (1 + 0.003 * flutter)) / sr
    x = np.zeros(n)
    for k, a in ((1, 1.0), (2, 0.32), (3, 0.14), (4, 0.05)):
        if freq * k < 0.45 * sr:
            x += a * np.sin(k * ph)
    x *= 1 + 0.1 * flutter
    chiff = 0.18 * norm(bandpass(rng.standard_normal(n), freq * 1.5, min(freq * 5, 0.45 * sr), sr)) * np.exp(-t / 0.012)
    return (x + chiff) * env(n, 0.012, min(0.06, dur * 0.3), sr)


def organ_bass(freq, dur, sr=LOOP_SR):
    """The band organ's bass pipe: a soft, round "oom", with enough of its
    overtones for a phone to carry it."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) + 0.75 * partial(2 * freq, t, sr) + 0.5 * partial(3 * freq, t, sr)
         + 0.25 * partial(4 * freq, t, sr)) * np.exp(-t / (dur * 0.6))
    return x * env(len(t), 0.012, 0.06, sr)


def pizz(freq, dur=0.5, sr=LOOP_SR, pos=0.14):
    """A pizzicato string, plucked with a finger: it rings only a moment,
    the high harmonics dying first; low notes ring a little longer."""
    t = t_of(dur, sr)
    tau = min(0.3, 0.07 + 50 / freq)
    x = np.zeros_like(t)
    for k in range(1, 9):
        x += abs(np.sin(np.pi * k * pos)) / k * partial(freq * k, t, sr) * np.exp(-t * (1 + 0.7 * (k - 1)) / tau)
    return x * env(len(t), 0.0012, 0.04, sr)


def chop(chord, at, amp, rng, sr=LOOP_SR):
    """The ukulele chopped on the off-beat: a quick strum, damped at once (chk)."""
    tones = chord_tones(chord, "E4")
    parts = [(at + 0.007 * k, amp * (1 - 0.06 * k) * uke(f, 0.13, sr, bright=0.5)) for k, f in enumerate(tones)]
    n = int(0.04 * sr)
    chk = norm(bandpass(rng.standard_normal(n), 1200, 5000, sr)) * np.exp(-np.arange(n) / (0.006 * sr))
    parts.append((at, 0.35 * amp * chk * env(n, 0.0005, 0.01, sr)))
    return parts


def guitar(freq, dur=1.5, sr=LOOP_SR, pos=0.2, bright=0.8):
    """A nylon-string guitar picked with the fingers: warmer and longer than
    the ukulele, the high harmonics fading first and a hair sharp (a real
    string is a little stiff)."""
    t = t_of(dur, sr)
    x = np.zeros_like(t)
    for k in range(1, 11):
        a = abs(np.sin(np.pi * k * pos)) / k ** 1.2
        x += (a if k == 1 else a * bright) * partial(freq * k * (1 + 0.0003 * k * k), t, sr) \
            * np.exp(-t / (dur * 0.33 / (1 + 0.4 * (k - 1))))
    return x * env(len(t), 0.003, 0.06, sr)


def flute(freq, dur, rng, sr=LOOP_SR):
    """A soft wooden flute: nearly a pure tone with a little breath in it, a
    puff of air as each note starts, a slow vibrato on long notes."""
    t = t_of(dur, sr)
    n = len(t)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.0 * t) * ease((t - 0.2) / 0.3)
    ph = 2 * np.pi * np.cumsum(freq * vib) / sr
    x = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
    breath = 0.05 * norm(resonator(rng.standard_normal(n), freq * 2, 500, sr))
    chiff = 0.2 * norm(bandpass(rng.standard_normal(n), freq * 1.5, freq * 4, sr)) * np.exp(-t / 0.015)
    return (x + breath + chiff) * env(n, 0.035, min(0.12, dur * 0.4), sr)


def plink(freq, dur=0.25, sr=LOOP_SR):
    """A little glassy plink, like a bead dropped on a toy block."""
    t = t_of(dur, sr)
    x = partial(freq, t, sr) * np.exp(-t / 0.05) + 0.3 * partial(freq * 2.76, t, sr) * np.exp(-t / 0.012)
    return x * env(len(t), 0.0008, 0.03, sr)


def clack(rng, sr=LOOP_SR, dur=0.06):
    """Two wooden blocks knocked together: a short, hollow clack."""
    n = int(dur * sr)
    t = np.arange(n) / sr
    hit = rng.standard_normal(n) * np.exp(-t / 0.002)
    x = norm(resonator(hit, 1250, 120, sr)) + 0.6 * norm(resonator(hit, 2650, 200, sr))
    return x * np.exp(-t / 0.018) * env(n, 0.0005, 0.015, sr)


def slide_whistle(f0, f1, dur, sr=LOOP_SR):
    """A slide whistle: a pure, breathy tone gliding from [f0] to [f1]."""
    t = t_of(dur, sr)
    f = f0 * (f1 / f0) ** ease(t / dur) * (1 + 0.006 * np.sin(2 * np.pi * 6 * t))
    ph = 2 * np.pi * np.cumsum(f) / sr
    return (np.sin(ph) + 0.08 * np.sin(2 * ph)) * env(len(t), 0.06, 0.1, sr)


def toy_horn(freq, dur, sr=SR):
    """A soft toy trumpet: every harmonic, the high ones quieter, opening up
    as it speaks; a little vibrato on a long note."""
    t = t_of(dur, sr)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * ease((t - 0.15) / 0.2)
    ph = 2 * np.pi * np.cumsum(freq * vib) / sr
    opening = ease(t / 0.05)
    x = np.zeros_like(t)
    for k in range(1, 9):
        if freq * k < 0.4 * sr:
            x += (1 if k == 1 else opening) / k ** 1.4 * np.sin(k * ph)
    return lowpass(x, 3500, sr) * env(len(t), 0.015, min(0.1, dur * 0.4), sr)


def spring(f0, dur, wobble=0.12, sr=SR):
    """A cartoon spring: it shoots up, wobbles, settles (畫畫小鎮's boing)."""
    t = t_of(dur, sr)
    f = f0 * (1 + 1.0 * (1 - np.exp(-t / 0.03))) * (1 + wobble * np.sin(2 * np.pi * 14 * t) * np.exp(-t / 0.15))
    return (sweep(f, sr) + 0.2 * sweep(2 * f, sr)) * env(len(t), 0.003, 0.06, sr) * decay(len(t), dur * 0.4, sr)


def hum(chord, length, low="G3", sr=LOOP_SR):
    """A warm pad: the chord held, swelling in and out, two tones a hair apart."""
    d = length + 1.0
    t = t_of(d, sr)
    swell = np.sin(np.pi * t / d) ** 2
    return sum(np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * f * 1.002 * t) for f in chord_tones(chord, low)[:3]) * swell


# ---------------------------------------------------------------- music


def music_park():
    """The park map: a gentle merry-go-round waltz in D, three beats a bar.
    The band organ's flute pipes sing the tune with a soft piccolo pipe an
    octave up; under it the oom-pah-pah: a round bass pipe on one, a short
    soft chord on two and three. In the second half a glockenspiel joins the
    tune, as on a real carousel. The last bar walks up A-C#-E back to the start."""
    beat = 0.35
    bars = ["D", "D", "G", "D", "Em", "A7", "D", "A7", "D", "D7", "G", "Gm", "D", "A7", "D", "A7"]
    tune = [("D5", 1), ("F#5", 1), ("A5", 1),
            ("D6", 2), ("A5", 1),
            ("B5", 2), ("G5", 1),
            ("A5", 2), ("F#5", 1),
            ("G5", 1), ("B5", 1), ("G5", 1),
            ("E5", 2), ("C#5", 1),
            ("D5", 1), ("E5", 1), ("F#5", 1),
            ("E5", 3),
            ("D5", 1), ("F#5", 1), ("A5", 1),
            ("C6", 2), ("A5", 1),
            ("B5", 1), ("D6", 1), ("B5", 1),
            ("Bb5", 2), ("G5", 1),
            ("F#5", 1), ("A5", 1), ("F#5", 1),
            ("E5", 1), ("A5", 1), ("G5", 1),
            ("D5", 2), (None, 1),
            ("A4", 1), ("C#5", 1), ("E5", 1)]
    rng = np.random.default_rng(111)
    notes = []
    for at, n, d in melody(tune, beat, bars=16, beats_per_bar=3):
        f = NOTE[n]
        notes += [(at, 0.5 * calliope(f, d * 0.94, rng)), (at, 0.09 * calliope(2 * f, d * 0.94, rng))]
        if at >= 24 * beat - 1e-9:  # the second half: the glockenspiel joins in
            notes.append((at, 0.12 * bell(2 * f, 0.7, LOOP_SR, bright=0.4)))
    for b, _, chord in spans(bars, 3):
        notes.append((b * beat, 0.6 * organ_bass(NOTE[above(root_of(chord), "A2")], 0.5)))
        notes.append((b * beat, 0.08 * kick()))
        for k in (1, 2):
            for f in chord_tones(chord, "A3"):
                notes.append(((b + k) * beat, 0.18 * calliope(f, 0.2, rng)))
    for b in (0, 24):  # a soft triangle at the top of each half
        notes.append((b * beat, 0.05 * metal(3100, 0.8, LOOP_SR, ratios=(1, 2.7, 4.1), amps=(1, .4, .2), taus=(.5, .2, .1))))
    x = tune_loop(len(bars) * 3 * beat, notes)
    return lowpass(x, 3800, LOOP_SR)


def music_city():
    """卡通城: a bouncy cartoon tune in B flat. Pizzicato strings play a
    jumpy tune full of little rests; a glockenspiel twinkles along the second
    time, and a ukulele joins it in bars 9-10. Boom-chick underneath: a
    plucked bass on one and three (walking up into each new phrase), the
    ukulele chopping on two and four. A soft drum, wood blocks and a shaker
    keep it light; temple blocks go tock-tock at the end of each phrase, and
    a slide whistle goes wheee up into the start again."""
    beat = 0.4
    bars = ["Bb", "Gm", "Eb", "F", "Bb", "Gm", "Cm-F", "Bb", "Eb", "Bb", "C7", "F"]
    tune = [("F5", .5), (None, .5), ("D5", .5), ("F5", .5), ("Bb5", 1), (None, 1),
            ("A5", .5), ("Bb5", .5), ("A5", .5), ("G5", .5), ("D5", 1), (None, 1),
            ("G5", .5), (None, .5), ("Eb5", .5), ("G5", .5), ("Bb5", 1), ("C6", .5), ("Bb5", .5),
            ("A5", 1), ("F5", .5), (None, .5), ("C5", 1), (None, 1),
            ("F5", .5), (None, .5), ("D5", .5), ("F5", .5), ("Bb5", .5), ("C6", .5), ("D6", 1),
            ("D6", .5), ("C6", .5), ("Bb5", .5), ("A5", .5), ("G5", 1), ("D5", 1),
            ("Eb5", .5), ("G5", .5), ("C6", 1), ("A5", .5), ("C6", .5), ("F5", 1),
            ("Bb5", 1), (None, .5), ("F5", .5), ("Bb5", 1), (None, 1),
            ("G5", .5), ("G5", .5), ("Bb5", .5), ("G5", .5), ("Eb5", 1), (None, 1),
            ("F5", .5), ("F5", .5), ("Bb5", .5), ("F5", .5), ("D5", 1), (None, 1),
            ("E5", .5), ("G5", .5), ("Bb5", .5), ("C6", .5), ("D6", .5), ("C6", .5), ("Bb5", .5), ("G5", .5),
            ("A5", 1), ("F5", .5), (None, 2.5)]
    rng = np.random.default_rng(112)
    notes = []
    for at, n, _ in melody(tune, beat, bars=12):
        f = NOTE[n]
        notes.append((at, 0.6 * pizz(f, 0.5)))
        b = at / beat
        if 16 <= b < 32 or b >= 40:  # the second time round: the glockenspiel twinkles along
            notes.append((at, 0.1 * bell(2 * f, 0.5, LOOP_SR, bright=0.5)))
        if 32 <= b < 40:  # bars 9-10: the ukulele sings along
            notes.append((at, 0.3 * uke(f, 0.5, bright=0.7)))
    roots = [root_of(c) for _, _, c in spans(bars, 4)]
    for i, (b, length, chord) in enumerate(spans(bars, 4)):
        bass = NOTE[above(root_of(chord), "E2")]
        notes.append((b * beat, 0.5 * pluck_bass(bass, 0.4)))
        if length == 4:
            fifth = bass * 2 ** (7 / 12)
            notes.append(((b + 2) * beat, 0.4 * pluck_bass(fifth / 2 if fifth > NOTE["D3"] else fifth, 0.35)))
        for off in ((1, 3) if length == 4 else (1,)):
            notes += chop(chord, (b + off) * beat, 0.16, rng)
        if b + length in (16, 32, 48):  # walk up into the next phrase: a semitone under its root
            nxt = NOTE[above(roots[(i + 1) % len(roots)], "E2")] * 2 ** (-1 / 12)
            notes.append(((b + length - 0.5) * beat, 0.35 * pluck_bass(nxt, 0.25)))
    beats = len(bars) * 4
    for b in range(beats):
        if b % 2 == 0:
            notes.append((b * beat, 0.22 * kick()))
        else:
            notes.append((b * beat, 0.07 * woodblock(1200 if b % 4 == 1 else 900)))
        notes.append(((b + 0.5) * beat, 0.035 * shaker(rng)))
    for b in (15, 31):  # temple blocks at the end of each phrase
        notes += [(b * beat, 0.13 * woodblock(720, dur=0.12)), ((b + 0.5) * beat, 0.13 * woodblock(960, dur=0.12))]
    notes.append((46 * beat, 0.16 * slide_whistle(NOTE["F5"], NOTE["F6"], 1.8 * beat)))
    x = tune_loop(beats * beat, notes)
    return lowpass(x, 5000, LOOP_SR)


def music_forest():
    """紙片森林: warm and cosy, in E, six quavers a bar (6/8). A nylon guitar
    is fingerpicked all the way through, a soft bass under each bar and a
    warm hum holding the chord. A kalimba sings the tune first; then a little
    wooden flute takes it, the kalimba twinkling a note in each bar and a
    small run at the end of each phrase. A shaker brushes softly."""
    eighth = 0.25
    bars = ["E", "C#m", "A", "B", "E", "G#m", "A", "B", "A", "B", "G#m-C#m", "F#m-B"]
    tune = [("G#5", 2), ("F#5", 1), ("E5", 2), ("B4", 1),
            ("C#5", 2), ("E5", 1), ("G#5", 3),
            ("A5", 2), ("G#5", 1), ("F#5", 2), ("E5", 1),
            ("F#5", 5), (None, 1),
            ("G#5", 2), ("F#5", 1), ("E5", 2), ("B4", 1),
            ("B4", 2), ("D#5", 1), ("G#5", 3),
            ("A5", 2), ("B5", 1), ("C#6", 2), ("A5", 1),
            ("B5", 5), (None, 1),
            ("C#6", 2), ("B5", 1), ("A5", 2), ("F#5", 1),
            ("B5", 2), ("A5", 1), ("F#5", 2), ("D#5", 1),
            ("G#5", 3), ("E5", 2), ("C#5", 1),
            ("A5", 2), ("F#5", 1), ("D#5", 1), ("E5", 1), ("F#5", 1)]
    rng = np.random.default_rng(113)
    notes = []
    for at, n, d in melody(tune, eighth, bars=12, beats_per_bar=6):
        f = NOTE[n]
        if at < 24 * eighth - 1e-9:  # bars 1-4: the kalimba
            notes.append((at, 0.55 * kalimba(f, max(1.4, d + 0.8))))
        else:  # bars 5-12: the flute
            notes.append((at, 0.4 * flute(f, d * 0.95, rng)))
    for e, n in ((21, "B5"), (22, "D#6"), (23, "F#6"), (45, "F#6"), (46, "D#6"), (47, "B5")):
        notes.append((e * eighth, 0.24 * kalimba(NOTE[n], 1.2)))
    for e, length, chord in spans(bars, 6):
        r = NOTE[above(root_of(chord), "E3")]
        t3 = 12 + third_of(chord)
        steps = [0, 7, 12, t3, 12, 7] if length == 6 else [0, 7, t3]
        for k, s in enumerate(steps):
            notes.append(((e + k) * eighth, (0.26 if k == 0 else 0.16) * guitar(r * 2 ** (s / 12), 1.3)))
        notes.append((e * eighth, 0.28 * pluck_bass(NOTE[above(root_of(chord), "E2")], 1.4)))
        notes.append((e * eighth, 0.018 * hum(chord, length * eighth)))
        if e >= 24 and length == 6:  # the kalimba twinkles once a bar under the flute
            notes.append(((e + 3) * eighth, 0.13 * kalimba(chord_tones(chord, "E6")[0], 1.0)))
    for e in range(len(bars) * 6):
        notes.append((e * eighth, (0.03 if e % 3 == 0 else 0.012) * shaker(rng, dur=0.08)))
    x = tune_loop(len(bars) * 6 * eighth, notes)
    return lowpass(x, 3600, LOOP_SR)


def music_blocks():
    """積木王國: tidy and playful, in C. A xylophone plays a tune made of
    little patterns (the same shape on each chord, like blocks in a row); in
    the second half a marimba plays along a third below. A marimba bass
    bounces in 3+3+2. Wooden blocks clack on two and four, a high wood tick
    on every off-beat, and little glassy plinks drop in at the end of each
    bar, with a run of them at the end of each half."""
    beat = 0.54
    bars = ["C", "F", "C", "G", "Am", "F", "Dm", "G"]
    tune = [("E5", .5), ("G5", .5), ("C6", 1), ("G5", .5), ("E5", .5), ("G5", 1),
            ("F5", .5), ("A5", .5), ("C6", 1), ("A5", .5), ("F5", .5), ("A5", 1),
            ("G5", .5), ("E5", .5), ("C5", 1), ("E5", .5), ("G5", .5), ("C6", 1),
            ("B5", .5), ("A5", .5), ("G5", 1), ("D5", 1), (None, 1),
            ("C6", .5), ("A5", .5), ("E5", 1), ("C6", .5), ("A5", .5), ("E5", 1),
            ("C6", .5), ("A5", .5), ("F5", 1), ("A5", .5), ("C6", .5), ("D6", 1),
            ("D6", .5), ("C6", .5), ("A5", 1), ("F5", 1), ("D5", 1),
            ("G5", .5), ("B5", .5), ("D6", 1), (None, 2)]
    rng = np.random.default_rng(114)
    notes = []
    for at, n, _ in melody(tune, beat, bars=8):
        notes.append((at, 0.6 * xylo(NOTE[n], 0.45)))
        if at >= 16 * beat - 1e-9:  # the second half: a marimba a third below
            notes.append((at, 0.3 * marimba(NOTE[third_below(n)], 0.5, LOOP_SR)))
    for b, _, chord in spans(bars, 4):
        r = chord_tones(chord, "C3")
        for off, f, a in ((0, r[0], 0.45), (1.5, r[2], 0.34), (3, 2 * r[0], 0.32)):
            notes.append(((b + off) * beat, a * marimba(f, 0.6, LOOP_SR)))
        if b not in (12, 28):  # a plink at the end of the bar (the runs take bars 4 and 8)
            notes.append(((b + 3.5) * beat, 0.12 * plink(chord_tones(chord, "C6")[2])))
    for b, n in ((15, "G6"), (15 + 1 / 3, "B6"), (15 + 2 / 3, "D7"),
                 (30, "G6"), (30.5, "B6"), (31, "D7"), (31.5, "G7")):
        notes.append((b * beat, 0.14 * plink(NOTE[n])))
    beats = len(bars) * 4
    for b in range(beats):
        if b % 2:
            notes.append((b * beat, 0.09 * clack(rng)))
        notes.append(((b + 0.5) * beat, 0.03 * woodblock(2300, dur=0.05)))
    x = tune_loop(beats * beat, notes)
    return lowpass(x, 5200, LOOP_SR)


def music_rest():
    """Rest time: a slow lullaby in E flat, six quavers a bar, rocking. A
    music box sings; a felt piano rocks low-high-low under it; a plucked
    bass and a warm hum hold each chord; a celesta twinkles at the end."""
    eighth = 0.375
    bars = ["Eb", "Cm", "Ab", "Bb", "Eb", "Ab", "Fm", "Bb"]
    tune = [("Bb5", 3), ("G5", 2), ("Eb5", 1),
            ("Eb5", 2), ("G5", 1), ("C6", 3),
            ("C6", 2), ("Bb5", 1), ("Ab5", 2), ("F5", 1),
            ("F5", 2), ("G5", 1), ("F5", 3),
            ("Bb5", 3), ("G5", 2), ("Eb5", 1),
            ("C6", 2), ("Ab5", 1), ("Eb5", 3),
            ("F5", 2), ("Ab5", 1), ("C6", 2), ("Ab5", 1),
            ("D5", 2), ("Eb5", 1), ("F5", 3)]
    notes = [(at, 0.7 * music_box_note(NOTE[n], 2.6, bright=0.4))
             for at, n, _ in melody(tune, eighth, bars=8, beats_per_bar=6)]
    for e, _, chord in spans(bars, 6):
        r = NOTE[above(root_of(chord), "Eb3")]
        t3 = 12 + third_of(chord)
        for k, s in enumerate([0, 7, 12, t3, 12, 7]):
            notes.append(((e + k) * eighth, (0.3 if k == 0 else 0.2) * soft_piano(r * 2 ** (s / 12), 1.8)))
        notes.append((e * eighth, 0.2 * pluck_bass(NOTE[above(root_of(chord), "E2")], 2.2)))
        notes.append((e * eighth, 0.035 * hum(chord, 6 * eighth)))
    notes += [(46 * eighth, 0.12 * celesta(NOTE["Bb6"], 1.4)), (47 * eighth, 0.1 * celesta(NOTE["F6"], 1.4))]
    x = tune_loop(len(bars) * 6 * eighth, notes)
    return lowpass(x, 2600, LOOP_SR)


# name: (make, loudness in dB beside the short sounds: about 8 under them).
MUSIC = {
    "music_park": (music_park, -8.5),
    "music_city": (music_city, -8),
    "music_forest": (music_forest, -8),
    "music_blocks": (music_blocks, -8),
    "music_rest": (music_rest, -9),
}


# ---------------------------------------------------------------- playing


def tap():
    """A button: a soft wooden tok."""
    t = t_of(0.07)
    x = (partial(980, t, SR) * np.exp(-t / 0.014) + 0.35 * partial(2350, t, SR) * np.exp(-t / 0.005)
         + 0.15 * partial(3900, t, SR) * np.exp(-t / 0.002))
    return x * env(len(t), 0.0008, 0.02)


def pick():
    """Lifting a thing up: a soft, round bloop that rises."""
    t = t_of(0.17)
    f = 330 * 2.8 ** ease(t / 0.12)
    x = sweep(f) + 0.18 * sweep(2 * f)
    return lowpass(x * env(len(t), 0.006, 0.07) * np.exp(-t / 0.1), 3000)


def drop():
    """Putting it down: a soft pop as it settles, with a little thud."""
    rng = np.random.default_rng(202)
    t = t_of(0.15)
    n = len(t)
    f = np.interp(t, [0, 0.02, 0.15], [720, 430, 370])
    body = (sweep(f) + 0.25 * sweep(2 * f)) * np.exp(-t / 0.035)
    thud = sweep(np.geomspace(190, 120, n)) * np.exp(-t / 0.03)
    click = 0.25 * norm(bandpass(rng.standard_normal(n), 1000, 5000)) * np.exp(-t / 0.0015)
    return carry((body + 0.6 * thud + click) * env(n, 0.001, 0.03), 0.2)


def right():
    """A right answer: a happy chime. A celesta and a glockenspiel run up
    G-C-E, di-di-ding, and land on a warm, shimmering C chord, with a tiny
    sparkle on top."""
    parts = []
    for k, n in enumerate(["G5", "C6", "E6"]):
        parts += [(0.075 * k, (0.45 + 0.05 * k) * celesta(NOTE[n], 0.45, SR)),
                  (0.075 * k, 0.15 * bell(NOTE[n] * 2, 0.3, bright=0.3))]
    land = 0.23
    parts += [(land, 0.5 * chime(NOTE["G6"], 0.95)), (land, 0.32 * chime(NOTE["C6"], 0.95)),
              (land, 0.28 * chime(NOTE["E6"], 0.95)), (land, 0.4 * celesta(NOTE["C6"], 0.8, SR))]
    parts += [(land + 0.12, 0.12 * bell(NOTE["C7"], 0.4, bright=0.3)), (land + 0.2, 0.09 * bell(NOTE["E7"], 0.35, bright=0.3))]
    return lowpass(place(1.2, parts), 7000)


def try_again():
    """Not there: a gentle, friendly "uh-oh". Two round notes going down a
    little, the second with a soft spring wobble (a boing). Never a buzzer."""
    def note(f, dur, wobble=0.0):
        t = t_of(dur)
        fr = f * (1 + wobble * np.sin(2 * np.pi * 9 * t) * np.exp(-t / 0.18) * ease(t / 0.05))
        ph = 2 * np.pi * np.cumsum(fr) / SR
        return (np.sin(ph) + 0.12 * np.sin(2 * ph) + 0.03 * np.sin(3 * ph)) * env(len(t), 0.025, dur * 0.45)
    x = place(0.62, [(0, 0.85 * note(NOTE["G5"], 0.16)), (0.2, note(NOTE["E5"], 0.4, 0.035))])
    return lowpass(x, 2000)


def bounce():
    """A thing springing back to the floor: boing-boing (and a tiny third),
    each landing with a soft tap."""
    def floor(a):
        t = t_of(0.05)
        return a * (partial(620, t, SR) * np.exp(-t / 0.01) + 0.3 * partial(1500, t, SR) * np.exp(-t / 0.004)) * env(len(t), 0.0008, 0.015)
    parts = [(0, floor(0.5)), (0, spring(260, 0.32)),
             (0.33, floor(0.4)), (0.33, 0.7 * spring(300, 0.24)),
             (0.56, floor(0.25)), (0.56, 0.4 * spring(340, 0.15))]
    return lowpass(place(0.75, parts), 4000)


def sparkle():
    """Something shining: a little shower of high bells, quickening, with a
    soft shimmer of air."""
    rng = np.random.default_rng(206)
    scale = ["C7", "D7", "E7", "G7", "A7", "C8"]
    parts, at = [], 0.0
    for k in range(10):
        n = scale[min(len(scale) - 1, int(k * 0.6 + rng.integers(0, 2)))]
        parts.append((at, (0.5 - 0.03 * k) * bell(NOTE[n], 0.3, bright=0.35)))
        at += 0.06 - 0.003 * k
    m = int(0.6 * SR)
    shimmer = norm(bandpass(rng.standard_normal(m), 6000, 9500)) * np.sin(np.pi * np.arange(m) / m) ** 2
    return place(0.75, parts + [(0, 0.06 * shimmer)])


def sticker():
    """A sticker: peeled off its sheet (a quick sticky fwip going up) and
    patted down (a soft pat)."""
    rng = np.random.default_rng(207)
    dur = 0.14
    t = t_of(dur)
    n = len(t)
    shape = ease(t / 0.1) * (1 - ease((t - 0.11) / 0.03))
    fwip = noise_through(rng, np.interp(t, [0, dur], [1300, 5200]), 1400, n)
    crackle = np.zeros(n)
    for i in rng.integers(0, n - 60, 18):
        crackle[i:i + 60] += rng.uniform(0.3, 1) * np.exp(-np.arange(60) / 8)
    peel = (fwip + 0.5 * norm(bandpass(crackle, 2500, 8000))) * shape
    t2 = t_of(0.08)
    pat = (0.7 * norm(lowpass(rng.standard_normal(len(t2)), 1500)) * np.exp(-t2 / 0.01)
           + 0.5 * sweep(np.geomspace(380, 250, len(t2))) * np.exp(-t2 / 0.02)) * env(len(t2), 0.001, 0.02)
    return place(0.33, [(0, 0.7 * peel), (0.19, 0.8 * pat)])


def star():
    """A star: a twinkle running up the glockenspiel, then a shimmer."""
    run = ["D6", "F#6", "A6", "D7"]
    parts = [(i * 0.055, (0.5 + 0.1 * i) * bell(NOTE[n], 0.5, bright=0.6)) for i, n in enumerate(run)]
    parts += [(0.26 + k * 0.06, 0.32 * 0.8 ** k * bell(NOTE["A6" if k % 2 else "D7"], 0.3, bright=0.3)) for k in range(8)]
    return place(0.95, parts)


def solved():
    """A case solved: ta-da-da-DAA! A toy trumpet and a xylophone run up
    G-C-E and land on a big C chord with a ukulele strum, a plucked bass and
    a tambourine, then a shower of sparkles. 1.5 s."""
    rng = np.random.default_rng(210)
    parts = []
    for n, at in (("G4", 0.0), ("C5", 0.1), ("E5", 0.2)):
        parts += [(at, 0.32 * toy_horn(NOTE[n], 0.12)), (at, 0.45 * xylo(NOTE[n], 0.3, SR))]
    land = 0.32
    parts += [(land, a * toy_horn(NOTE[n], 0.75)) for n, a in (("G5", 0.38), ("E5", 0.24), ("C5", 0.24))]
    parts += [(land, 0.5 * xylo(NOTE["C6"], 0.8, SR)), (land, 0.2 * bell(NOTE["C7"], 0.9, bright=0.5)),
              (land, 0.4 * pluck_bass(NOTE["C3"], 0.9, SR)), (land, 0.25 * jingle(rng))]
    parts += [(land + 0.012 * k, 0.2 * uke(NOTE[n], 0.9, SR, bright=0.6)) for k, n in enumerate(["G4", "C5", "E5", "G5"])]
    for k, n in enumerate(["G6", "C7", "E7", "D7", "G7", "E7", "C8"]):
        parts.append((0.62 + 0.085 * k + rng.uniform(-0.015, 0.015), (0.22 - 0.02 * k) * bell(NOTE[n], 0.35, bright=0.4)))
    return place(1.5, parts)


def poof():
    """阿布 changing his look: a puff of smoke, pfff, with a soft low whump
    and three tiny magic twinkles inside it."""
    rng = np.random.default_rng(211)
    dur = 0.5
    t = t_of(dur)
    n = len(t)
    shape = ease(t / 0.012) * np.exp(-t / 0.11)
    air = noise_through(rng, glide(t, (0, 2200), (dur, 500)), 1500, n)
    soft = norm(lowpass(rng.standard_normal(n), 900))
    whump = sweep(np.geomspace(260, 120, n)) * np.exp(-t / 0.05)
    x = carry((0.6 * air + 0.5 * soft) * shape + 0.35 * whump * env(n, 0.003, 0.05), 0.15)
    tw = [(0.15 + 0.06 * k, 0.1 * bell(NOTE[m], 0.25, bright=0.3)) for k, m in enumerate(["E7", "G7", "C8"])]
    return place(0.55, [(0, x)] + tw)


def crayon():
    """Drawing a line: a crayon scribbling on paper, shh-shh, waxy and grainy."""
    rng = np.random.default_rng(212)

    def stroke(dur, lo, hi):
        n = int(dur * SR)
        t = np.arange(n) / SR
        grain = 0.55 + 0.45 * norm(lowpass(rng.standard_normal(n), 140))  # the wax catching the paper
        x = norm(bandpass(rng.standard_normal(n), lo, hi)) * np.abs(grain)
        return x * np.sin(np.pi * t / dur) ** 0.7
    return place(0.4, [(0, stroke(0.17, 2200, 7000)), (0.2, 0.85 * stroke(0.16, 1900, 6200))])


def snap():
    """A line joined: a neat little click, with a tiny ting to say "done"."""
    rng = np.random.default_rng(213)
    t = t_of(0.08)
    n = len(t)
    click = 0.6 * norm(highpass(rng.standard_normal(n), 2000)) * np.exp(-t / 0.0012)
    tok = partial(1400, t, SR) * np.exp(-t / 0.012) + 0.4 * partial(3200, t, SR) * np.exp(-t / 0.004)
    snap_ = (click + tok) * env(n, 0.0005, 0.02)
    return place(0.3, [(0, snap_), (0.03, 0.25 * bell(NOTE["G6"], 0.26, bright=0.3))])


def train():
    """The block train arriving: two puffs of steam, then a tiny toy whistle,
    choo-choo!"""
    rng = np.random.default_rng(214)
    parts = []
    for at, a in ((0, 0.45), (0.17, 0.35)):
        m = int(0.15 * SR)
        tm = np.arange(m) / SR
        puff = norm(bandpass(rng.standard_normal(m), 400, 3500)) * ease(tm / 0.008) * np.exp(-tm / 0.05)
        parts.append((at, a * puff))

    def whistle(dur):
        t = t_of(dur)
        scoop = 1 - 0.04 * np.exp(-t / 0.03)
        x = sum(sweep(f * scoop) + 0.2 * sweep(2 * f * scoop) for f in (NOTE["A5"], NOTE["C#6"], NOTE["E6"]))
        air = 0.35 * norm(bandpass(rng.standard_normal(len(t)), 800, 3000))
        return (x / 3 + 0.25 * air) * env(len(t), 0.02, 0.06)
    parts += [(0.36, 0.55 * whistle(0.13)), (0.53, 0.6 * whistle(0.28))]
    return place(0.85, parts)


def clue():
    """The magnifying glass: a quick whoosh up, then a bright ding with a glint."""
    rng = np.random.default_rng(215)
    dur = 0.24
    t = t_of(dur)
    n = len(t)
    whoosh = noise_through(rng, np.interp(t, [0, dur], [500, 3500]), 900, n) * np.sin(np.pi * t / dur) ** 2
    t2 = t_of(0.95)
    f = NOTE["A6"]
    ding = ((np.sin(2 * np.pi * f * t2) + 0.5 * np.sin(2 * np.pi * f * 1.004 * t2)) * np.exp(-t2 / 0.35)
            + 0.35 * np.sin(2 * np.pi * f * 2.41 * t2) * np.exp(-t2 / 0.12)
            + 0.12 * np.sin(2 * np.pi * f * 4.13 * t2) * np.exp(-t2 / 0.04)) * env(len(t2), 0.001, 0.1)
    return place(1.15, [(0, 0.5 * whoosh), (0.18, 0.6 * ding), (0.26, 0.12 * bell(NOTE["E7"], 0.4, bright=0.3))])


def blub():
    """A fish in the toy box: blub-blub-blub (going down, as if puzzled),
    then a big wobbly bloo-OOP as it jumps out, and a few bubbles."""
    rng = np.random.default_rng(216)

    def gulp(f0, f1, dur):
        t = t_of(dur)
        f = np.geomspace(f0, f1, len(t))
        return (sweep(f) + 0.3 * sweep(2 * f)) * env(len(t), 0.004, 0.03) * decay(len(t), dur * 0.5)
    t = t_of(0.24)
    f = 200 * 5.5 ** ease(t / 0.2) * (1 + 0.08 * np.sin(2 * np.pi * 16 * t))
    big = (sweep(f) + 0.35 * sweep(2 * f)) * env(len(t), 0.01, 0.05)
    parts = [(0, gulp(520, 1000, 0.07)), (0.09, gulp(440, 880, 0.07)), (0.18, gulp(360, 760, 0.08)), (0.3, 0.9 * big)]
    parts += [(0.56 + 0.05 * k, 0.25 * bubble(rng, SR, (700, 1100), (1.8, 2.4), (0.025, 0.04))) for k in range(3)]
    return place(0.75, parts)


def giggle():
    """A funny moment: hee-hee-hee-hee, a run of short, high, voiced notes,
    stepping down and bouncing back up."""
    rng = np.random.default_rng(217)
    pitches = [700, 660, 700, 620, 590, 640]
    parts = []
    for k, f in enumerate(pitches):
        dur = 0.07 if k < len(pitches) - 1 else 0.12
        t = t_of(dur)
        f0 = np.linspace(f * 1.06, f * 0.92, len(t))
        x = voice(f0, [(820, 140, 1.0), (2500, 240, 0.55), (3400, 300, 0.15)], rng, breath=0.12)
        x *= np.sin(np.pi * t / dur) ** 0.8
        m = int(0.025 * SR)
        h = norm(bandpass(rng.standard_normal(m), 1500, 5500)) * np.hanning(m) * 0.15  # the "h"
        at = k * 0.1 + rng.uniform(-0.008, 0.008) + 0.01
        parts += [(at, h), (at + 0.018, x)]
    return place(0.75, parts)


def garbage_truck():
    """The garbage truck's tune: the opening of Für Elise (Beethoven, 1810),
    from a tinny little loudspeaker, as Taiwan's garbage trucks play it."""
    tune = [("E5", 1), ("D#5", 1), ("E5", 1), ("D#5", 1), ("E5", 1), ("B4", 1), ("D5", 1), ("C5", 1), ("A4", 2)]
    beat, parts, at = 0.14, [], 0.0
    for note, beats in tune:
        dur = beat * beats
        t = t_of(dur)
        f = NOTE[note]
        x = triangle(f, dur) + 0.35 * np.sign(np.sin(2 * np.pi * f * t))
        parts.append((at, x * env(len(t), 0.008, 0.06) * (decay(len(t), 0.5) if beats > 1 else 1)))
        at += dur
    return bandpass(place(at + 0.1, parts), 450, 3800)


def rest_time():
    """Time to rest: a soft yawn (a breathy aah sinking to oh), then a warm
    chime and a quieter one below it."""
    rng = np.random.default_rng(219)
    dur = 0.9
    t = t_of(dur)
    f0 = glide(t, (0, 330), (0.15, 420), (0.6, 300), (dur, 230))
    f1 = glide(t, (0, 500), (0.2, 850), (0.6, 750), (dur, 560))
    f2 = glide(t, (0, 1250), (0.2, 1300), (dur, 950))
    yawn = voice(f0, [(f1, 140, 1.0), (f2, 180, 0.5), (2800, 300, 0.08)], rng, breath=0.3) * env(len(t), 0.1, 0.35)
    return place(1.5, [(0, 0.8 * yawn), (0.72, 0.5 * chime(NOTE["G5"], 0.78)), (0.92, 0.3 * chime(NOTE["C5"], 0.58))])


def abu_hmm():
    """阿布 thinking: a closed-mouth "hmm?", curious, rising at the end like a question."""
    rng = np.random.default_rng(220)
    dur = 0.52
    t = t_of(dur)
    f0 = glide(t, (0, 300), (0.25, 285), (0.42, 380), (dur, 410)) * (1 + 0.01 * np.sin(2 * np.pi * 5.5 * t))
    x = voice(f0, [(300, 90, 1.0), (1000, 150, 0.3), (2200, 250, 0.1)], rng, breath=0.04)
    return carry(lowpass(x, 2500) * env(len(t), 0.04, 0.12), 0.35, lo=500, hi=2500)


def abu_yay():
    """阿布 cheering: a short, bright "ya!", jumping up."""
    rng = np.random.default_rng(221)
    dur = 0.32
    t = t_of(dur)
    f0 = glide(t, (0, 420), (0.08, 570), (dur, 480))
    f1 = np.interp(t, [0, 0.07, dur], [320, 880, 820])
    f2 = np.interp(t, [0, 0.07, dur], [2300, 1500, 1400])
    x = voice(f0, [(f1, 120, 1.0), (f2, 160, 0.6), (3000, 300, 0.12)], rng, breath=0.05)
    return x * env(len(t), 0.012, 0.12)


# ---------------------------------------------------------------- thank-you voices

VOWEL = {"i": (300, 2300, 3000), "e": (480, 1950, 2800), "a": (850, 1400, 2700), "o": (500, 900, 2600), "u": (350, 800, 2400)}


def syllable(rng, dur, f0, f1, v0, v1, size=1.0, fric=0.0, nasal=False):
    """One sung syllable: pitch [f0] to [f1], the vowel [v0] turning to [v1];
    [size] scales the mouth (above 1 is a smaller, younger voice); [fric] a
    soft "sh" before it (like 謝 xiè); [nasal] an "n" before it."""
    t = t_of(dur)
    pitch = glide(t, (0, f0), (dur, f1))
    turn = ease(t / (0.45 * dur))
    fs = [size * (np.array(VOWEL[v0][i]) * (1 - turn) + VOWEL[v1][i] * turn) for i in range(3)]
    x = voice(pitch, [(fs[0], 120, 1.0), (fs[1], 170, 0.55), (fs[2], 260, 0.15)], rng, breath=0.06)
    if nasal:
        x *= 0.35 + 0.65 * ease((t - 0.02) / 0.05)
        x = x + 0.5 * norm(lowpass(voice(pitch, [(280, 80, 1.0)], rng), 900)) * (1 - ease((t - 0.02) / 0.05))
    x *= env(len(t), 0.012, 0.06)
    if not fric:
        return x
    m = int(0.05 * SR)
    sh = fric * norm(bandpass(rng.standard_normal(m), 3000, 7500)) * np.sin(np.pi * np.arange(m) / m) ** 1.5
    return place(0.04 + dur, [(0, sh), (0.04, x)])


def thanks_a():
    """A cheerful, light voice: "xiè-xie!", two syllables, the second jumping up."""
    rng = np.random.default_rng(231)
    return place(0.62, [(0, syllable(rng, 0.17, 560, 450, "i", "e", 1.12, 0.3)),
                        (0.22, syllable(rng, 0.28, 600, 720, "i", "e", 1.12, 0.25))])


def thanks_b():
    """A warm, lower, grown-up voice: "xiè-xie-nǐ!", three syllables, the
    last one rising."""
    rng = np.random.default_rng(232)
    return carry(place(0.82, [(0, syllable(rng, 0.17, 300, 235, "i", "e", 0.95, 0.3)),
                              (0.2, syllable(rng, 0.13, 255, 245, "i", "e", 0.95, 0.2)),
                              (0.38, syllable(rng, 0.36, 260, 360, "i", "i", 0.95, nasal=True))]), 0.25)


def thanks_c():
    """A bouncy, sing-song voice: "xiè-xiè-la!", three quick notes up an arpeggio."""
    rng = np.random.default_rng(233)
    return place(0.72, [(0, syllable(rng, 0.12, NOTE["E5"], NOTE["E5"] * 0.95, "i", "e", 1.15, 0.25)),
                        (0.17, syllable(rng, 0.12, NOTE["G5"], NOTE["G5"] * 0.97, "i", "e", 1.15, 0.2)),
                        (0.33, syllable(rng, 0.3, NOTE["C6"], NOTE["C6"] * 1.03, "a", "a", 1.1))])


# ---------------------------------------------------------------- animals and the baby


def woof(rng, high=1.0, times=2):
    """A dog: woof woof."""
    def one():
        dur = 0.16 / high ** 0.3
        t = t_of(dur)
        f0 = glide(t, (0, 330), (0.04, 380), (dur, 220)) * high
        x = voice(f0, [(520 * high ** 0.5, 160, 1.0), (1350 * high ** 0.4, 220, 0.5), (2600, 300, 0.1)], rng, breath=0.3, rough=0.05)
        return x * env(len(t), 0.004, 0.06) * decay(len(t), 0.09)
    return place(0.23 * times + 0.1, [(0.23 * i, one()) for i in range(times)])


def say_dog():
    """汪汪: a happy young dog with its bone, woof woof."""
    return woof(np.random.default_rng(301), high=1.22)


def say_cat():
    """喵: a cute mi-aa-ow."""
    rng = np.random.default_rng(302)
    dur = 0.72
    t = t_of(dur)
    f0 = glide(t, (0, 520), (0.27, 760), (dur, 480)) * 1.1
    f1 = glide(t, (0, 320), (0.24, 900), (dur, 450))
    f2 = glide(t, (0, 2300), (0.29, 1500), (dur, 950))
    return voice(f0, [(f1, 120, 1.0), (f2, 180, 0.6), (3000, 300, 0.1)], rng, breath=0.05) * env(len(t), 0.05, 0.2)


def say_rabbit():
    """A rabbit with its carrot: nibble-nibble-nibble, crunchy little bites,
    twice, then a tiny happy squeak."""
    rng = np.random.default_rng(303)

    def bite(amp):
        m = int(0.03 * SR)
        tm = np.arange(m) / SR
        crunch = np.zeros(m)
        for i in rng.integers(0, m - 40, 6):
            crunch[i:i + 40] += rng.uniform(0.4, 1) * np.exp(-np.arange(40) / 6) * rng.choice([-1, 1])
        x = norm(resonator(crunch, 2300, 500)) + 0.6 * norm(bandpass(crunch, 3000, 8000))
        return amp * x * np.exp(-tm / 0.012) * env(m, 0.0008, 0.008)

    def squeak(dur, f):
        t = t_of(dur)
        fr = np.interp(t, [0, 0.4 * dur, dur], [f, f * 1.3, f * 1.12])
        return (sweep(fr) + 0.15 * sweep(2 * fr)) * np.sin(np.pi * t / dur) ** 1.2
    parts = [(0.0, bite(0.8)), (0.06, bite(0.65)), (0.12, bite(0.75)),
             (0.27, bite(0.8)), (0.33, bite(0.6)), (0.39, bite(0.7)),
             (0.52, 0.45 * squeak(0.1, 1600))]
    return place(0.66, parts)


def say_baby():
    """A baby with its bottle: shake-shake goes the rattle, then a little
    giggle, a-ha-ha."""
    rng = np.random.default_rng(304)

    def shake(dur):
        n = int(dur * SR)
        beads = np.zeros(n)
        for i in rng.integers(0, n - 150, 26):
            beads[i:i + 150] += rng.uniform(0.3, 1) * bandpass(rng.standard_normal(150), 2500, 8000) * np.exp(-np.arange(150) / 12)
        shell = norm(resonator(beads, 1900, 300))  # the hollow plastic ball
        return (norm(beads) + 0.5 * shell) * np.sin(np.pi * np.arange(n) / n) ** 0.5
    parts = [(0, 0.55 * shake(0.13)), (0.19, 0.5 * shake(0.12))]
    for k, f in enumerate([500, 560, 480]):
        dur = 0.08 if k < 2 else 0.12
        t = t_of(dur)
        x = voice(np.linspace(f * 1.05, f * 0.93, len(t)), [(1000, 160, 1.0), (1900, 220, 0.5), (3200, 300, 0.12)], rng, breath=0.15)
        parts.append((0.42 + 0.11 * k, 0.8 * x * np.sin(np.pi * t / dur) ** 0.8))
    return place(0.82, parts)


def say_cow():
    """哞～: mmm-ooo, rising then sinking, a little higher than a real cow."""
    rng = np.random.default_rng(305)
    low, dur = 1.15, 1.1
    t = t_of(dur)
    f0 = glide(t, (0, 105), (0.25 * dur, 150), (0.7 * dur, 140), (dur, 96)) * low * (1 + 0.012 * np.sin(2 * np.pi * 5 * t))
    opening = ease((t - 0.08) / 0.25)  # the mouth opens from "m" to "oo-oh"
    x = voice(f0, [(250 + 380 * opening * low, 90, 1.0), (600 + 350 * opening * low, 120, 0.45), (2400, 250, 0.06)], rng, breath=0.04)
    return carry(x * env(len(t), 0.1, 0.3), 0.3)


def say_sheep():
    """咩～: b-aa-aa, a lamb's bleat."""
    rng = np.random.default_rng(306)
    high, dur, shake = 1.12, 0.85, 7.0
    t = t_of(dur)
    bleat = 1 + 0.05 * np.sin(2 * np.pi * shake * t) * ease(t / 0.2)
    f0 = glide(t, (0, 250), (0.12, 300), (dur, 255)) * high * bleat
    opening = ease(t / 0.06)
    x = voice(f0, [(350 + 450 * opening, 110, 1.0), (1150 + 150 * high, 150, 0.6), (2600, 250, 0.12)], rng, breath=0.05)
    return x * env(len(t), 0.01, 0.25) * (0.75 + 0.25 * np.sin(2 * np.pi * shake * t))


def say_bird():
    """啾啾: a little bird, tweet-tweet and a tiny trill."""
    def chirp(dur, lo, hi):
        t = t_of(dur)
        f = np.interp(t, [0, 0.35 * dur, dur], [lo, hi, lo * 1.15])
        return sweep(f) * np.sin(np.pi * t / dur) ** 1.5
    parts = [(0, chirp(0.09, 2700, 4300)), (0.15, chirp(0.1, 2800, 4400))]
    parts += [(0.36 + 0.045 * k, 0.5 * chirp(0.035, 3300 + 200 * (k % 2), 3900)) for k in range(4)]
    return place(0.58, parts)


def say_hen():
    """咕咕: a hen, bok, bok, bok, b-gawk!"""
    rng = np.random.default_rng(308)

    def bok(dur=0.07, f=380):
        t = t_of(dur)
        x = voice(np.full(len(t), float(f)), [(650, 140, 1.0), (1500, 200, 0.4)], rng, breath=0.2)
        return x * env(len(t), 0.003, 0.04) * decay(len(t), 0.04)
    t = t_of(0.34)
    f0 = glide(t, (0, 480), (0.08, 650), (0.34, 470))
    gawk = voice(f0, [(glide(t, (0, 450), (0.1, 750), (0.34, 650)), 140, 1.0), (1200, 200, 0.5)], rng, breath=0.15)
    return place(0.82, [(0, bok()), (0.13, bok(f=400)), (0.26, bok(f=370)), (0.44, gawk * env(len(t), 0.01, 0.12))])


def say_bee():
    """A bee with its hive: bzz... bzzzz, a cute buzz with fluttering wings,
    flying a little closer and away."""
    n = int(0.95 * SR)
    t = np.arange(n) / SR
    f = glide(t, (0, 225), (0.3, 250), (0.6, 265), (0.95, 235)) * (1 + 0.025 * np.sin(2 * np.pi * 7 * t))
    x = bandpass(harmonics(f, tilt=1.0), 300, 3000) * (0.75 + 0.25 * np.sin(2 * np.pi * 32 * t))
    shape = ease(t / 0.05) * (1 - ease((t - 0.22) / 0.06)) + ease((t - 0.33) / 0.08) * (1 - ease((t - 0.7) / 0.25))
    return x * shape * env(n, 0.005, 0.03)


def say_frog():
    """呱呱: a frog, ribbit, ribbit: a buzzy croak that rattles, in two parts."""
    rng = np.random.default_rng(310)

    def syl(dur, f0, form):
        t = t_of(dur)
        x = voice(np.interp(t, [0, dur], [f0, f0 * 1.08]), [(form, 160, 1.0), (form * 1.9, 250, 0.5), (500, 120, 0.2)],
                  rng, breath=0.1)
        return x * (0.65 + 0.35 * np.sin(2 * np.pi * 38 * t)) * env(len(t), 0.006, 0.03)

    def ribbit(at):
        return [(at, syl(0.1, 150, 950)), (at + 0.13, 0.85 * syl(0.08, 170, 1150))]
    return round_off(place(0.75, ribbit(0) + ribbit(0.38)), 1.5)


def say_duck():
    """A rubber duck: squeak! as it is squeezed, and a softer squee as it
    lets go."""
    rng = np.random.default_rng(311)

    def squeak(dur, f0, f1, f2):
        t = t_of(dur)
        f = np.interp(t, [0, 0.3 * dur, dur], [f0, f1, f2]) * (1 + 0.012 * np.sin(2 * np.pi * 45 * t))
        tone = harmonics(f, tilt=1.1)
        x = bandpass(tone, 900, 4500) + 0.6 * norm(resonator(tone, 2600, 400))
        air = 0.12 * norm(bandpass(rng.standard_normal(len(t)), 2000, 7000))
        return (norm(x) + air) * env(len(t), 0.01, 0.04) * (0.7 + 0.3 * np.sin(np.pi * t / dur))
    return lowpass(place(0.45, [(0, squeak(0.17, 1000, 1350, 1250)), (0.24, 0.75 * squeak(0.13, 1250, 1150, 1000))]), 5000)


def say_monkey():
    """A monkey with its banana: ooh ooh aah aah!"""
    rng = np.random.default_rng(312)

    def one(f, vowel, dur=0.14):
        t = t_of(dur)
        f0 = glide(t, (0, f * 0.9), (dur, f * 1.1))
        f1, f2 = (380, 800) if vowel == "oo" else (850, 1350)
        return voice(f0, [(f1, 130, 1.0), (f2, 180, 0.5), (2600, 300, 0.08)], rng, breath=0.08) * env(len(t), 0.01, 0.05)
    return place(0.82, [(0, one(480, "oo")), (0.17, one(560, "oo")), (0.36, one(720, "aa", 0.17)), (0.58, one(820, "aa", 0.2))])


def say_squirrel():
    """A squirrel with its nut: a quick chitter, chk-chk-chk-chk, chk-chk-chk, kee!"""
    rng = np.random.default_rng(313)

    def chit(f, dur=0.03):
        t = t_of(dur)
        fr = np.geomspace(f * 1.25, f * 0.8, len(t))
        click = 0.4 * norm(bandpass(rng.standard_normal(len(t)), 3000, 8000)) * np.exp(-t / 0.002)
        return (sweep(fr) + 0.2 * sweep(2 * fr) + click) * np.sin(np.pi * t / dur) ** 0.8
    parts = [(0.055 * k, (0.8 - 0.08 * k) * chit(3000 + 120 * (k % 2))) for k in range(4)]
    parts += [(0.3 + 0.05 * k, (0.75 - 0.08 * k) * chit(3150 - 100 * (k % 2))) for k in range(3)]
    t = t_of(0.09)
    kee = sweep(np.interp(t, [0, 0.03, 0.09], [3300, 3800, 3200])) * np.sin(np.pi * t / 0.09)
    return place(0.6, parts + [(0.49, 0.7 * kee)])


def say_octopus():
    """An octopus: bloop-bloop, two big, round, wobbly bubbles, and a few
    small ones after."""
    rng = np.random.default_rng(314)

    def bloop(f0, f1, dur):
        t = t_of(dur)
        f = f0 * (f1 / f0) ** ease(t / (0.8 * dur)) * (1 + 0.06 * np.sin(2 * np.pi * 18 * t) * np.exp(-t / 0.12))
        x = sweep(f) + 0.45 * sweep(2 * f) + 0.15 * sweep(3 * f)
        return x * env(len(t), 0.008, 0.06) * decay(len(t), dur * 0.6)
    parts = [(0, bloop(200, 520, 0.24)), (0.27, 0.9 * bloop(240, 640, 0.26))]
    parts += [(0.56 + 0.06 * k + rng.uniform(0, 0.02), 0.22 * bubble(rng, SR, (600, 1000), (1.8, 2.4), (0.025, 0.04))) for k in range(4)]
    return carry(place(0.85, parts), 0.25)


def say_fish():
    """A fish back in the water: one soft blub, then a stream of little
    bubbles going up."""
    rng = np.random.default_rng(315)
    t = t_of(0.09)
    f = np.geomspace(320, 820, len(t))
    blub_ = (sweep(f) + 0.3 * sweep(2 * f)) * env(len(t), 0.004, 0.03) * decay(len(t), 0.045)
    parts = [(0, 0.7 * blub_)]
    parts += [(at, rng.uniform(0.3, 0.6) * bubble(rng, SR, (600, 1100), (1.8, 2.6), (0.025, 0.045)))
              for at in np.sort(rng.uniform(0.08, 0.55, 9))]
    return place(0.62, parts)


# ---------------------------------------------------------------- the list

# name: (make, loudness in dB beside the others: below 0 sits softer).
EFFECTS = {
    "tap": (tap, -4), "pick": (pick, -4), "drop": (drop, -4), "right": (right, 0), "try": (try_again, -5),
    "bounce": (bounce, -2), "sparkle": (sparkle, -3), "sticker": (sticker, -3), "star": (star, -1),
    "solved": (solved, 0), "poof": (poof, -2), "crayon": (crayon, -5), "snap": (snap, -3), "train": (train, -1),
    "clue": (clue, -1), "blub": (blub, -1), "giggle": (giggle, -1), "garbage_truck": (garbage_truck, -1),
    "rest": (rest_time, -2), "abu_hmm": (abu_hmm, -1), "abu_yay": (abu_yay, 0),
}
VOICES = {
    "thanks_a": (thanks_a, 0), "thanks_b": (thanks_b, 0), "thanks_c": (thanks_c, 0),
    "say_dog": (say_dog, 0), "say_cat": (say_cat, 0), "say_rabbit": (say_rabbit, -2), "say_baby": (say_baby, -1),
    "say_cow": (say_cow, 0), "say_sheep": (say_sheep, 0), "say_bird": (say_bird, -3), "say_hen": (say_hen, 0),
    "say_bee": (say_bee, -1), "say_frog": (say_frog, 0), "say_duck": (say_duck, -1), "say_monkey": (say_monkey, 0),
    "say_squirrel": (say_squirrel, -3), "say_octopus": (say_octopus, 0), "say_fish": (say_fish, -1),
}
SHORT = {**EFFECTS, **VOICES}
LONGEST = {**{k: 1.5 for k in EFFECTS}, **{k: 1.2 for k in VOICES}}  # seconds
TARGET = -21.0  # dB, the loudness of a short sound at 0 (about where the sibling apps' sit)
MAX_PEAK = 0.72


# ---------------------------------------------------------------- writing and checking


def tidy(x, sr=SR):
    """A short sound: drop the silent end, then fade both ends so neither clicks."""
    x = np.asarray(x, dtype=np.float64)
    loud = np.nonzero(np.abs(x) > np.abs(x).max() * 1e-3)[0]
    x = x[: min(len(x), loud[-1] + int(0.01 * sr))]
    return x * env(len(x), 0.002, 0.012, sr)


def phone_ready(x, sr=SR):
    """Take out what a phone cannot play anyway (under 70 Hz), for more room
    under the peak. The filter works on the whole sound at once and wraps
    round, so pad it with silence on both sides first: what it rings before
    the start and after the end then stays out of the sound (unpadded, the
    ring before a sharp start came round to the end as a tiny blip)."""
    pad = int(0.1 * sr)
    return highpass(np.concatenate([np.zeros(pad), x, np.zeros(pad)]), 70, sr)[pad:]


def level(x, offset, sr=SR):
    """[x] at the loudness TARGET + [offset] dB, unless that would put its
    peak over MAX_PEAK: then at MAX_PEAK. Returns the peak."""
    x = norm(x)
    return min(MAX_PEAK, 10 ** ((TARGET + offset - loudness(x, sr)) / 20))


def write(path, x, peak, sr):
    x = np.asarray(x, dtype=np.float64)
    x = x / max(1e-9, np.abs(x).max()) * peak
    data = np.round(x * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())
    return data


def seam(data, sr):
    """A loop's seam, checked two ways: the jump from the last sample back to
    the first (beside the usual step from one sample to the next), and the
    sound over 3 kHz in the 20 ms around the seam (a click would show as a
    burst there) beside the loudest 20 ms anywhere else in the loop."""
    x = data.astype(np.float64)
    steps = np.abs(np.diff(x))
    jump = abs(x[0] - x[-1])
    half = len(x) // 2
    h = highpass(np.roll(x, half), 3000, sr) ** 2  # the seam now sits at [half]
    w = int(0.02 * sr)
    c = np.concatenate([[0], np.cumsum(h)])
    starts = np.arange(0, len(h) - w + 1, w // 2)
    at = half - w // 2
    here = c[at + w] - c[at]
    others = (c[starts + w] - c[starts])[np.abs(starts - at) >= w]
    return jump, np.median(steps), np.percentile(steps, 99), here / max(1e-9, others.max())


def report(name, data, sr, loop, want=None):
    x = data.astype(np.float64) / 32767
    peak = np.abs(x).max()
    loud = loudness(x, sr)
    clipped = int(np.sum(np.abs(data) >= 32767))
    if loop:
        jump, usual, p99, burst = seam(data, sr)
        edge = f"seam jump {jump:4.0f} (usual step {usual:.0f}, 99% {p99:.0f}), seam highs {burst:.2f} of the loudest elsewhere"
    else:
        edge = f"ends {int(data[0]):+d} / {int(data[-1]):+d}"
    short = "" if want is None or loud > want - 0.5 else f"  ({want - loud:.1f} dB under, held by the peak)"
    print(f"  {name:15s} {len(x) / sr:5.2f} s  {len(data) * 2 + 44:9,d} bytes  peak {peak:.2f}  "
          f"loudness {loud:6.1f} dB  clipped {clipped}  {edge}{short}")


def read(path):
    with wave.open(str(path), "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float64) / 32767, w.getframerate()


def preview(path, loop_seconds=8.0, gap=0.5):
    """A listening preview: [loop_seconds] of each tune, then every short
    sound in order, [gap] apart. Prints where each one starts."""
    path = pathlib.Path(path)
    sr, pieces, at = 22050, [], 0.0
    print(f"preview {path}:")
    for name in list(MUSIC) + list(SHORT):
        x, rate = read(OUT / f"{name}.wav")
        if rate != sr:
            x = resample_poly(x, sr, rate)
        if name in MUSIC:
            x = x[: int(loop_seconds * sr)] * env(int(loop_seconds * sr), 0.01, 0.5, sr)
        print(f"  {int(at // 60)}:{at % 60:04.1f}  {name}")
        pieces += [x, np.zeros(int((1.0 if name in MUSIC else gap) * sr))]
        at += (len(x) + len(pieces[-1])) / sr
    wav = path.with_suffix(".wav")
    write(wav, np.concatenate(pieces), np.abs(np.concatenate(pieces)).max(), sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "aac", "-b:a", "96k", str(path)], check=True)
    wav.unlink()
    print(f"  total {at:.1f} s")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".keep").unlink(missing_ok=True)
    print("music (16,000 Hz, loops), about 8 dB under the short sounds:")
    for name, (make, offset) in MUSIC.items():
        x = make()
        assert 16 <= len(x) / LOOP_SR <= 20, (name, len(x) / LOOP_SR)
        report(name, write(OUT / f"{name}.wav", x, level(x, offset, LOOP_SR), LOOP_SR), LOOP_SR, True)
    print(f"short sounds (22,050 Hz), loudness {TARGET:.0f} dB plus or minus, peaks at most {MAX_PEAK}:")
    for name, (make, offset) in SHORT.items():
        x = tidy(phone_ready(make()))
        assert len(x) / SR <= LONGEST[name], (name, len(x) / SR)
        data = write(OUT / f"{name}.wav", x, level(x, offset), SR)
        assert data[0] == 0 and data[-1] == 0, name
        report(name, data, SR, False, TARGET + offset)
    names = {p.stem for p in OUT.glob("*.wav")}
    assert names == set(MUSIC) | set(SHORT), names ^ (set(MUSIC) | set(SHORT))
    total = sum(p.stat().st_size for p in OUT.glob("*.wav"))
    print(f"{len(MUSIC) + len(SHORT)} sounds, {total:,} bytes ({total / 1024 / 1024:.2f} MiB) in {OUT}")
    assert total < LIMIT, f"the sounds must stay under {LIMIT:,} bytes"
    if len(sys.argv) == 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])


if __name__ == "__main__":
    main()
