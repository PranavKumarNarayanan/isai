# CLI for Isai MIDI Generator.
import argparse, time
from core.scales import NOTES, INTERVALS
from engine.mood import MOODS, get_tempo
from engine.arrangement import arrange
from midi_export import arr_to_midi

def main():
    p = argparse.ArgumentParser(description='Isai — Procedural MIDI Generator')
    p.add_argument('--root', default='C', choices=NOTES)
    p.add_argument('--scale', default='major', choices=list(INTERVALS.keys()))
    p.add_argument('--mood', default='happy', choices=list(MOODS.keys()))
    p.add_argument('--complexity', type=int, default=3, choices=[1,2,3,4,5])
    p.add_argument('--tempo', type=int)
    p.add_argument('--bars', type=int, default=16)
    p.add_argument('--seed', type=int)
    p.add_argument('--output', '-o')
    a = p.parse_args()
    s = a.seed if a.seed is not None else int(time.time() * 1000) % (2**31)
    out = a.output if a.output else f"{a.root}_{a.scale}_{a.mood}_c{a.complexity}.mid"
    print(f"🎵 Isai | {a.root} {a.scale} | {a.mood} | C{a.complexity} | Seed: {s}")
    arr = arrange(a.root, a.scale, a.mood, a.complexity, a.bars, a.tempo, s)
    arr_to_midi(arr, out)
    print(f"✅ Saved: {out} | {arr['tempo']} BPM")

if __name__ == '__main__':
    main()
