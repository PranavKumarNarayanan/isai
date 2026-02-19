"""
CLI entry point for headless MIDI generation.

Usage:
    python generate.py --root C --scale minor --mood sad --complexity 3 --bars 16 --output my_song.mid
"""
import argparse
import random
import time

from core.scales import NOTE_NAMES, SCALE_INTERVALS
from engine.mood import get_mood_profile, suggest_tempo, MOOD_PROFILES
from engine.arrangement import arrange
from midi_export import arrangement_to_midi


def main():
    parser = argparse.ArgumentParser(
        description='Isai — Procedural MIDI Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate.py --root C --scale major --mood happy
  python generate.py --root A --scale pentatonic_minor --mood dreamy --complexity 4 --bars 32
  python generate.py --root E --scale blues --mood dark --tempo 90 --output blues_jam.mid
        """
    )
    parser.add_argument('--root', type=str, default='C',
                        choices=[n for n in NOTE_NAMES],
                        help='Root note (default: C)')
    parser.add_argument('--scale', type=str, default='major',
                        choices=list(SCALE_INTERVALS.keys()),
                        help='Scale type (default: major)')
    parser.add_argument('--mood', type=str, default='happy',
                        choices=list(MOOD_PROFILES.keys()),
                        help='Mood (default: happy)')
    parser.add_argument('--complexity', type=int, default=3,
                        choices=[1, 2, 3, 4, 5],
                        help='Complexity level 1-5 (default: 3)')
    parser.add_argument('--tempo', type=int, default=None,
                        help='BPM (default: auto from mood)')
    parser.add_argument('--bars', type=int, default=16,
                        help='Number of bars (default: 16)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output file path (default: auto-generated name)')

    args = parser.parse_args()

    if args.seed is None:
        args.seed = int(time.time() * 1000) % (2**31)

    if args.output is None:
        args.output = f"{args.root}_{args.scale}_{args.mood}_c{args.complexity}.mid"

    print(f"🎵 Isai — Procedural MIDI Generator")
    print(f"   Root: {args.root} | Scale: {args.scale} | Mood: {args.mood}")
    print(f"   Complexity: {args.complexity} | Bars: {args.bars}")
    if args.tempo:
        print(f"   Tempo: {args.tempo} BPM")
    else:
        print(f"   Tempo: auto (~{suggest_tempo(args.mood)} BPM)")
    print(f"   Seed: {args.seed}")
    print()

    print("Generating arrangement...")
    arrangement = arrange(
        root=args.root,
        scale_type=args.scale,
        mood=args.mood,
        complexity=args.complexity,
        total_bars=args.bars,
        tempo=args.tempo,
        seed=args.seed,
    )

    print("Exporting MIDI...")
    output_path = arrangement_to_midi(arrangement, args.output)

    sections = arrangement['sections']
    print(f"\n✅ Saved to: {output_path}")
    print(f"   Tempo: {arrangement['tempo']} BPM")
    print(f"   Structure: {' → '.join(s[0].capitalize() for s in sections)}")
    print(f"   Melody notes: {len(arrangement['tracks']['melody'])}")
    print(f"   Chord events: {len(arrangement['tracks']['chords'])}")
    print(f"   Bass events:  {len(arrangement['tracks']['bass'])}")


if __name__ == '__main__':
    main()
