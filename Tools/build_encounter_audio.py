"""Build original, conservative-level fishing encounter cues using the stdlib.

Run with ordinary Python. Outputs are mono PCM16, 44.1 kHz. The drag cue is
constructed on a circular timeline so the runtime can loop it continuously.
Runtime gain/pitch can convey fight intensity without changing the source file.
"""

from array import array
import json
import math
from pathlib import Path
import random
import sys
import wave


RATE = 44100
TAU = 2.0 * math.pi
OUT = Path(__file__).resolve().parents[1] / "ArtSource" / "Audio" / "Encounter"


def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3.0 - 2.0 * x)


def envelope(t, attack, decay):
    return smooth(t / attack) * math.exp(-max(0.0, t) / decay) if t >= 0.0 else 0.0


def filtered_noise(count, seed, cutoff):
    rng = random.Random(seed)
    coefficient = 1.0 - math.exp(-TAU * cutoff / RATE)
    previous = 0.0
    result = []
    for _ in range(count):
        previous += coefficient * (rng.uniform(-1.0, 1.0) - previous)
        result.append(previous)
    return result


def hook_set():
    duration = 0.44
    count = round(duration * RATE)
    body = filtered_noise(count, 4301, 1900.0)
    water = filtered_noise(count, 4302, 760.0)
    result = []
    for i in range(count):
        t = i / RATE
        snap_t = t - 0.012
        snap = 0.95 * body[i] * envelope(snap_t, 0.0015, 0.014)
        line = (math.sin(TAU * (225.0 * snap_t - 32.0 * snap_t * snap_t))
                + 0.31 * math.sin(TAU * 437.0 * snap_t))
        line *= 0.16 * envelope(snap_t, 0.002, 0.043)
        thump_t = t - 0.019
        thump = 0.28 * math.sin(TAU * (92.0 * thump_t - 62.0 * thump_t * thump_t))
        thump *= envelope(thump_t, 0.005, 0.055)
        splash = 0.65 * water[i] * envelope(t - 0.034, 0.012, 0.085)
        result.append(snap + line + thump + splash)
    return result, False, 0.60


def drag_run():
    duration = 1.0
    count = round(duration * RATE)
    rng = random.Random(4311)
    # These slightly uneven teeth repeat every second, including their tails.
    teeth = [(0.018 + k / 25.0 + rng.uniform(-0.0012, 0.0012),
              rng.uniform(0.82, 1.0)) for k in range(25)]
    harmonics = [(73, 0.014, 0.3), (151, 0.009, 1.1),
                 (227, 0.006, 2.9), (379, 0.003, 0.7)]
    result = []
    for i in range(count):
        t = i / RATE
        x = sum(gain * math.sin(TAU * frequency * t + phase)
                for frequency, gain, phase in harmonics)
        for onset, strength in teeth:
            age = (t - onset) % duration
            if age < 0.064:
                tail = smooth((0.064 - age) / 0.012)
                ring = (math.sin(TAU * 680.0 * age)
                        + 0.40 * math.sin(TAU * 1137.0 * age)
                        + 0.16 * math.sin(TAU * 1841.0 * age))
                x += strength * 0.28 * ring * envelope(age, 0.0009, 0.009) * tail
                x += strength * 0.085 * math.sin(TAU * 178.0 * age) * envelope(age, 0.002, 0.015) * tail
        result.append(x)
    return result, True, 0.42


def line_strain():
    duration = 0.61
    count = round(duration * RATE)
    friction = filtered_noise(count, 4321, 1050.0)
    result = []
    for i in range(count):
        t = i / RATE
        shaped = smooth(t / 0.065) * smooth((duration - t) / 0.19)
        phase = TAU * (171.0 * t + 92.0 * t * t / (2.0 * duration))
        roughness = 0.66 + 0.20 * math.sin(TAU * 23.0 * t) + 0.10 * math.sin(TAU * 37.0 * t)
        creak = (0.11 * math.sin(phase + 0.4 * math.sin(TAU * 31.0 * t))
                 + 0.048 * math.sin(phase * 2.017)
                 + 0.025 * math.sin(phase * 3.073))
        result.append(shaped * roughness * (creak + 0.36 * friction[i]))
    return result, False, 0.37


def escape():
    duration = 0.68
    count = round(duration * RATE)
    snap = filtered_noise(count, 4331, 1650.0)
    splash = filtered_noise(count, 4332, 1150.0)
    water = filtered_noise(count, 4333, 220.0)
    result = []
    for i in range(count):
        t = i / RATE
        x = 0.54 * snap[i] * envelope(t - 0.010, 0.0015, 0.014)
        x += 0.06 * math.sin(TAU * (265.0 * t - 170.0 * t * t)) * envelope(t, 0.002, 0.035)
        x += (0.72 * splash[i] + 0.55 * water[i]) * envelope(t - 0.085, 0.027, 0.13)
        for onset, frequency, gain in [(0.16, 430.0, 0.027), (0.24, 315.0, 0.022)]:
            age = t - onset
            x += gain * math.sin(TAU * (frequency * age - 180.0 * age * age)) * envelope(age, 0.004, 0.024)
        result.append(x)
    return result, False, 0.48


def trophy():
    duration = 1.88
    count = round(duration * RATE)
    felt = filtered_noise(count, 4341, 1400.0)
    # D major: four ascending, soft mallet notes followed by a quiet cadence.
    notes = [(0.025, 293.665, 0.22, 0.25), (0.205, 369.994, 0.21, 0.26),
             (0.385, 440.000, 0.20, 0.29), (0.585, 587.330, 0.20, 0.37),
             (0.805, 146.832, 0.14, 0.49), (0.805, 293.665, 0.11, 0.44),
             (0.805, 369.994, 0.09, 0.42), (0.805, 440.000, 0.08, 0.40)]
    result = []
    for i in range(count):
        t = i / RATE
        x = 0.0
        for onset, frequency, gain, decay in notes:
            age = t - onset
            if age >= 0.0:
                tone = math.sin(TAU * frequency * age)
                tone += 0.17 * math.sin(TAU * frequency * 2.003 * age) * math.exp(-age * 6.0)
                tone += 0.045 * math.sin(TAU * frequency * 3.997 * age) * math.exp(-age * 12.0)
                x += gain * tone * envelope(age, 0.006, decay)
                x += gain * 0.17 * felt[i] * envelope(age, 0.0015, 0.012)
                # A subdued, delayed reflection connects the phrase naturally.
                echo_age = age - 0.077
                if echo_age >= 0.0:
                    x += gain * 0.12 * math.sin(TAU * frequency * echo_age) * envelope(echo_age, 0.014, decay * 0.75)
        result.append(x)
    return result, False, 0.55


def write_cue(name, samples, looping, peak_target):
    # Remove tiny synthesis DC offsets, preserving periodicity for the drag cue.
    dc = sum(samples) / len(samples)
    samples = [x - dc for x in samples]
    if not looping:
        fade_in = round(0.001 * RATE)
        fade_out = round(0.045 * RATE)
        samples = [x * smooth(i / fade_in) * smooth((len(samples) - 1 - i) / fade_out)
                   for i, x in enumerate(samples)]
    peak = max(abs(x) for x in samples)
    gain = peak_target / peak if peak else 1.0
    pcm = array("h", (round(x * gain * 32767.0) for x in samples))
    if sys.byteorder != "little":
        pcm.byteswap()
    path = OUT / (name + ".wav")
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(pcm.tobytes())
    # Inspect the actual written PCM, not only the pre-quantized source.
    with wave.open(str(path), "rb") as source:
        checked = array("h", source.readframes(source.getnframes()))
        if sys.byteorder != "little":
            checked.byteswap()
        decoded = [x / 32768.0 for x in checked]
        metrics = {
            "name": name, "path": str(path), "duration_seconds": len(decoded) / RATE,
            "sample_rate": source.getframerate(), "channels": source.getnchannels(),
            "bits_per_sample": source.getsampwidth() * 8,
            "peak": round(max(abs(x) for x in decoded), 6),
            "rms": round(math.sqrt(sum(x * x for x in decoded) / len(decoded)), 6),
            "dc": round(sum(decoded) / len(decoded), 8), "looping": looping,
        }
        assert metrics["peak"] <= 0.65, metrics
        if looping:
            deltas = sorted(abs(decoded[i] - decoded[i - 1]) for i in range(1, len(decoded)))
            seam = abs(decoded[0] - decoded[-1])
            metrics["loop_seam_step"] = round(seam, 6)
            metrics["sample_step_p99"] = round(deltas[int(len(deltas) * 0.99)], 6)
            assert seam <= max(0.005, deltas[int(len(deltas) * 0.99)]), metrics
        else:
            assert checked[0] == 0 and checked[-1] == 0, name
    print(json.dumps(metrics))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, build in [("HookSet", hook_set), ("DragRun", drag_run),
                        ("LineStrain", line_strain), ("Escape", escape),
                        ("Trophy", trophy)]:
        write_cue(name, *build())


if __name__ == "__main__":
    main()
