# Chord voicing and progressions.
import random
from core.scales import INTERVALS, NOTES, name_to_midi, get_quality

VOICINGS = {
    'maj':[0,4,7], 'min':[0,3,7], 'dim':[0,3,6], 'aug':[0,4,8],
    'maj7':[0,4,7,11], 'min7':[0,3,7,10], 'dom7':[0,4,7,10], 'dim7':[0,3,6,9],
    'sus2':[0,2,7], 'sus4':[0,5,7]
}

TEMPLATES = {
    'happy':    [[0,4,5,3], [0,3,4,4], [0,4,3,5]],
    'sad':      [[0,5,2,6], [0,3,5,4], [0,2,3,4]],
    'energetic':[[0,4,3,5], [0,3,0,4], [0,4,5,3]],
    'calm':     [[0,3,4,0], [0,5,3,4], [0,2,3,0]],
    'dark':     [[0,5,4,3], [0,6,5,4], [0,3,6,4]],
    'epic':     [[0,5,3,4], [0,4,5,3], [5,3,0,4]],
    'dreamy':   [[0,2,5,3], [0,5,2,4], [3,0,5,2]]
}

SUBS = {'maj':['maj7','sus2'], 'min':['min7','sus4'], 'dim':['dim7'], 'aug':['maj7']}

def get_chord(root: int, q: str = 'maj') -> list[int]:
    # notes for root + quality.
    return [root + i for i in VOICINGS.get(q, VOICINGS['maj'])]

def get_prog(mood: str, type: str, root: str, oct: int = 3, comp: int = 1, bars: int = 4) -> list[list[int]]:
    # Generate chord progression.
    tmpl = random.choice(TEMPLATES.get(mood, TEMPLATES['happy']))
    ivs = INTERVALS[type]
    base = 12 * (oct + 1) + NOTES.index(root.upper())
    res = []
    for i in range(bars):
        deg = tmpl[i % len(tmpl)]
        r = base + ivs[deg % len(ivs)]
        q = get_quality(type, deg % len(ivs))
        if comp >= 3 and random.random() < 0.3 * (comp - 2) / 3:
            q = random.choice(SUBS.get(q, [q]))
        res.append(get_chord(r, q))
    return res

def arp(chord: list[int], pat: str = 'up', n: int = 4) -> list[int]:
    # Arpeggiate chord.
    if not chord: return []
    if pat == 'up': res = [chord[i % len(chord)] for i in range(n)]
    elif pat == 'down': res = [list(reversed(chord))[i % len(chord)] for i in range(n)]
    elif pat == 'updown':
        f = chord + list(reversed(chord[1:-1])) if len(chord) > 2 else chord
        res = [f[i % len(f)] for i in range(n)]
    else: res = [random.choice(chord) for _ in range(n)]
    return res
