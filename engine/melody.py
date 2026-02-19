"""
Melody generator: weighted random walk on scale degrees with
mood-driven interval selection, motif development, and complexity-aware ornamentation.
"""
import random
from core.scales import build_scale
from core.rhythm import (
    get_rhythm_pattern, humanize_velocity, humanize_timing,
    apply_mood_feel, TICKS_PER_BEAT, EIGHTH, SIXTEENTH
)
from engine.mood import get_mood_profile


def _pick_next_note(current_idx: int, scale: list[int], profile: dict,
                    complexity: int) -> int:
    """
    Weighted random walk: pick the next note index in the scale.
    Favours stepwise motion, with occasional leaps controlled by mood.
    """
    n = len(scale)
    if n <= 1:
        return 0

    weights = []
    for i in range(n):
        step = abs(i - current_idx)
        if step == 0:
            w = 1.0  # staying on same note
        elif step <= 2:
            w = 5.0  # stepwise
        elif step <= 4:
            w = 2.0 if random.random() < profile['leap_probability'] * 2 else 0.5
        else:
            w = 0.8 if random.random() < profile['leap_probability'] else 0.1

        # Direction bias
        if i > current_idx:
            w *= profile['direction_bias'] * 2
        elif i < current_idx:
            w *= (1 - profile['direction_bias']) * 2

        # Prefer notes in the mood's octave range
        note_octave = (scale[i] // 12) - 1
        oct_lo, oct_hi = profile['octave_range']
        if oct_lo <= note_octave <= oct_hi:
            w *= 2.0
        else:
            w *= 0.3

        weights.append(max(w, 0.01))

    # Normalize
    total = sum(weights)
    weights = [w / total for w in weights]

    return random.choices(range(n), weights=weights, k=1)[0]


def generate_motif(scale: list[int], profile: dict, length: int = 4,
                   start_idx: int = None) -> list[int]:
    """Generate a short melodic motif (sequence of scale indices)."""
    if start_idx is None:
        # Start near the middle of the comfortable range
        oct_lo, oct_hi = profile['octave_range']
        target_midi = 12 * ((oct_lo + oct_hi) // 2 + 1)
        start_idx = min(range(len(scale)),
                        key=lambda i: abs(scale[i] - target_midi))

    motif = [start_idx]
    for _ in range(length - 1):
        motif.append(_pick_next_note(motif[-1], scale, profile, 3))
    return motif


def develop_motif(motif: list[int], scale: list[int],
                  method: str = 'transpose') -> list[int]:
    """
    Develop a motif by transformation.
    Methods: 'transpose', 'invert', 'reverse', 'vary'
    """
    n = len(scale)
    if method == 'transpose':
        shift = random.choice([2, 3, 4, 5, -2, -3])
        return [max(0, min(n - 1, idx + shift)) for idx in motif]
    elif method == 'invert':
        pivot = motif[0]
        return [max(0, min(n - 1, pivot - (idx - pivot))) for idx in motif]
    elif method == 'reverse':
        return list(reversed(motif))
    elif method == 'vary':
        varied = list(motif)
        for i in range(len(varied)):
            if random.random() < 0.3:
                varied[i] = max(0, min(n - 1, varied[i] + random.choice([-1, 1])))
        return varied
    return motif


def generate_melody(root: str, scale_type: str, mood: str,
                    complexity: int, bars: int = 8,
                    seed: int = None) -> list[dict]:
    """
    Generate a melody track.

    Returns a list of note events:
        [{'note': midi_note, 'velocity': int, 'duration': ticks, 'time': absolute_tick}, ...]
    """
    if seed is not None:
        random.seed(seed)

    profile = get_mood_profile(mood)
    scale = build_scale(root, scale_type,
                        octave_start=profile['octave_range'][0],
                        octave_end=profile['octave_range'][1])
    if not scale:
        return []

    complexity = max(1, min(5, complexity))

    # Generate rhythm patterns
    rhythm_bars = get_rhythm_pattern(complexity, bars)

    # Generate a base motif
    motif = generate_motif(scale, profile, length=4)
    development_methods = ['transpose', 'invert', 'reverse', 'vary']

    events = []
    current_idx = motif[0]
    absolute_time = 0
    motif_counter = 0

    for bar_idx, bar_rhythm in enumerate(rhythm_bars):
        # Every few bars, use a developed motif
        if bar_idx % 4 == 0 and bar_idx > 0:
            method = development_methods[motif_counter % len(development_methods)]
            active_motif = develop_motif(motif, scale, method)
            motif_counter += 1
        elif bar_idx % 2 == 0:
            active_motif = list(motif)  # repeat original
        else:
            active_motif = None  # free walk

        motif_pos = 0

        for dur, vel_factor in bar_rhythm:
            # Decide if this slot gets a note or rest
            if random.random() > profile['note_density']:
                absolute_time += dur
                continue

            # Pick note
            if active_motif and motif_pos < len(active_motif):
                current_idx = active_motif[motif_pos]
                motif_pos += 1
            else:
                current_idx = _pick_next_note(current_idx, scale, profile, complexity)

            note = scale[current_idx]
            velocity = int(profile['base_velocity'] * vel_factor)
            velocity = humanize_velocity(velocity, profile['velocity_variance'])
            velocity, note_dur = apply_mood_feel(velocity, dur, mood)

            # At complexity 4+, occasionally add ornamental notes
            if complexity >= 4 and random.random() < 0.2:
                # Grace note before the main note
                grace_idx = max(0, min(len(scale) - 1, current_idx + random.choice([-1, 1])))
                grace_dur = SIXTEENTH
                events.append({
                    'note': scale[grace_idx],
                    'velocity': max(1, velocity - 15),
                    'duration': grace_dur,
                    'time': absolute_time,
                })
                absolute_time += grace_dur
                note_dur = max(SIXTEENTH, note_dur - grace_dur)

            # Humanize timing slightly
            actual_dur = humanize_timing(note_dur, 0.015)

            events.append({
                'note': note,
                'velocity': velocity,
                'duration': actual_dur,
                'time': absolute_time,
            })

            absolute_time += dur  # advance by the full rhythmic slot

    return events
