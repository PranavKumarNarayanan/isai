"""
Arrangement engine: combines melody, chords, and bass into a
multi-section song structure.
"""
import random
from core.scales import build_scale, SCALE_INTERVALS, NOTE_NAMES, note_name_to_midi
from core.chords import get_progression, arpeggiate_chord
from core.rhythm import (
    TICKS_PER_BEAT, WHOLE, HALF, QUARTER, EIGHTH,
    get_chord_rhythm, humanize_velocity
)
from engine.melody import generate_melody
from engine.mood import get_mood_profile

# Song section types
SECTION_STRUCTURES = {
    'short':  ['intro', 'verse', 'chorus', 'outro'],
    'medium': ['intro', 'verse', 'chorus', 'verse', 'chorus', 'outro'],
    'long':   ['intro', 'verse', 'prechorus', 'chorus', 'verse',
               'prechorus', 'chorus', 'bridge', 'chorus', 'outro'],
}

# Relative energy for each section (affects velocity and density)
SECTION_ENERGY = {
    'intro':     0.6,
    'verse':     0.75,
    'prechorus': 0.85,
    'chorus':    1.0,
    'bridge':    0.7,
    'outro':     0.5,
}


def _pick_structure(total_bars: int) -> list[str]:
    """Pick song structure based on total duration."""
    if total_bars <= 12:
        return SECTION_STRUCTURES['short']
    elif total_bars <= 32:
        return SECTION_STRUCTURES['medium']
    else:
        return SECTION_STRUCTURES['long']


def _divide_bars(total_bars: int, sections: list[str]) -> list[int]:
    """Distribute total bars across sections (min 2 bars per section)."""
    n = len(sections)
    base = max(2, total_bars // n)
    remainder = total_bars - base * n

    bar_counts = [base] * n
    # Give extra bars to chorus and verse sections
    priority = ['chorus', 'verse', 'bridge', 'prechorus', 'intro', 'outro']
    i = 0
    while remainder > 0:
        for sec_idx, sec_name in enumerate(sections):
            if sec_name == priority[i % len(priority)] and remainder > 0:
                bar_counts[sec_idx] += 1
                remainder -= 1
        i += 1
        if i > 100:
            break

    return bar_counts


def _generate_bass_line(chord_progression: list[list[int]],
                        chord_durations: list[int],
                        mood: str, complexity: int) -> list[dict]:
    """
    Generate a bass line from the chord roots.
    """
    profile = get_mood_profile(mood)
    events = []
    absolute_time = 0

    for chord, dur in zip(chord_progression, chord_durations):
        if not chord:
            absolute_time += dur
            continue

        bass_note = min(chord)  # lowest chord note
        # Drop to bass octave
        while bass_note > 48:
            bass_note -= 12

        velocity = humanize_velocity(int(profile['base_velocity'] * 0.85))

        if complexity >= 3 and dur >= HALF:
            # Walking bass: split into sub-notes
            steps = 2 if complexity < 4 else 4
            step_dur = dur // steps
            for s in range(steps):
                if s == 0:
                    n = bass_note
                else:
                    n = bass_note + random.choice([0, 2, 4, 5, 7])
                    while n > 55:
                        n -= 12
                events.append({
                    'note': n,
                    'velocity': velocity,
                    'duration': int(step_dur * 0.9),
                    'time': absolute_time,
                })
                absolute_time += step_dur
        else:
            events.append({
                'note': bass_note,
                'velocity': velocity,
                'duration': int(dur * 0.9),
                'time': absolute_time,
            })
            absolute_time += dur

    return events


def _generate_chord_track(chord_progression: list[list[int]],
                          chord_durations: list[int],
                          mood: str, complexity: int) -> list[dict]:
    """
    Generate chord accompaniment events.
    At higher complexity, uses arpeggiation.
    """
    profile = get_mood_profile(mood)
    events = []
    absolute_time = 0

    for chord, dur in zip(chord_progression, chord_durations):
        if not chord:
            absolute_time += dur
            continue

        velocity = humanize_velocity(int(profile['base_velocity'] * 0.7))

        if complexity >= 4:
            # Arpeggiate
            arp_notes = arpeggiate_chord(chord, profile['arp_pattern'],
                                         steps=dur // EIGHTH if dur >= QUARTER else 2)
            step_dur = dur // len(arp_notes) if arp_notes else dur
            for note in arp_notes:
                events.append({
                    'note': note,
                    'velocity': humanize_velocity(velocity),
                    'duration': int(step_dur * 0.85),
                    'time': absolute_time,
                })
                absolute_time += step_dur
        else:
            # Block chords
            for note in chord:
                events.append({
                    'note': note,
                    'velocity': velocity,
                    'duration': int(dur * 0.9),
                    'time': absolute_time,
                })
            absolute_time += dur

    return events


def arrange(root: str, scale_type: str, mood: str,
            complexity: int, total_bars: int = 16,
            tempo: int = None, seed: int = None) -> dict:
    """
    Generate a complete multi-track arrangement.

    Returns:
        {
            'tempo': int,
            'tracks': {
                'melody': [events...],
                'chords': [events...],
                'bass':   [events...],
            },
            'sections': [(name, bar_count), ...],
            'meta': { config info }
        }
    """
    if seed is not None:
        random.seed(seed)

    profile = get_mood_profile(mood)

    if tempo is None:
        lo, hi = profile['tempo_range']
        tempo = random.randint(lo, hi)

    complexity = max(1, min(5, complexity))
    total_bars = max(4, total_bars)

    # Determine structure
    sections = _pick_structure(total_bars)
    bar_counts = _divide_bars(total_bars, sections)

    melody_events = []
    chord_events = []
    bass_events = []

    bar_offset = 0
    ticks_per_bar = TICKS_PER_BEAT * 4  # 4/4 time

    for section_name, section_bars in zip(sections, bar_counts):
        energy = SECTION_ENERGY.get(section_name, 0.75)

        # Adjust complexity for section energy
        section_complexity = max(1, min(5, int(complexity * energy + 0.5)))

        tick_offset = bar_offset * ticks_per_bar

        # ── Melody ──
        section_melody = generate_melody(
            root, scale_type, mood,
            section_complexity, section_bars,
            seed=(seed + bar_offset) if seed else None
        )
        # Offset melody events to the current position
        for evt in section_melody:
            evt['time'] += tick_offset
            # Apply section energy to velocity
            evt['velocity'] = max(1, min(127, int(evt['velocity'] * energy)))
        melody_events.extend(section_melody)

        # ── Chords ──
        chords = get_progression(mood, scale_type, root,
                                  octave=3, complexity=section_complexity,
                                  bars=section_bars)
        chord_durs = get_chord_rhythm(section_complexity, section_bars)

        # Align chord count to duration count
        min_len = min(len(chords), len(chord_durs))
        chords = chords[:min_len]
        chord_durs = chord_durs[:min_len]

        section_chords = _generate_chord_track(chords, chord_durs, mood, section_complexity)
        for evt in section_chords:
            evt['time'] += tick_offset
            evt['velocity'] = max(1, min(127, int(evt['velocity'] * energy)))
        chord_events.extend(section_chords)

        # ── Bass ──
        section_bass = _generate_bass_line(chords, chord_durs, mood, section_complexity)
        for evt in section_bass:
            evt['time'] += tick_offset
            evt['velocity'] = max(1, min(127, int(evt['velocity'] * energy)))
        bass_events.extend(section_bass)

        bar_offset += section_bars

    return {
        'tempo': tempo,
        'tracks': {
            'melody': melody_events,
            'chords': chord_events,
            'bass': bass_events,
        },
        'sections': list(zip(sections, bar_counts)),
        'meta': {
            'root': root,
            'scale': scale_type,
            'mood': mood,
            'complexity': complexity,
            'total_bars': total_bars,
            'tempo': tempo,
        }
    }
