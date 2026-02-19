# Rhythm patterns and timing.
import random

TPB = 480 # ticks per beat
W, H, Q, E, S = TPB*4, TPB*2, TPB, TPB//2, TPB//4
DQ, DE, TQ = int(TPB*1.5), int(TPB*0.75), int(TPB*2/3)

PATS = {
    1: [[(W, 1.0)], [(H, 1.0), (H, 0.85)], [(H, 1.0), (Q, 0.9), (Q, 0.85)]],
    2: [[(Q, 1.0), (Q, 0.8), (Q, 0.9), (Q, 0.8)], [(H, 1.0), (Q, 0.85), (Q, 0.9)], [(Q, 1.0), (H, 0.85), (Q, 0.9)], [(DQ, 1.0), (E, 0.75), (H, 0.9)]],
    3: [[(Q, 1.0), (E, 0.8), (E, 0.75), (Q, 0.9), (Q, 0.85)], [(E, 1.0), (E, 0.7), (Q, 0.9), (E, 0.8), (E, 0.7), (Q, 0.85)], [(DQ, 1.0), (E, 0.7), (Q, 0.9), (E, 0.75), (E, 0.7)]],
    4: [[(E, 1.0), (DQ, 0.85), (E, 0.8), (E, 0.75), (Q, 0.9)], [(S, 0.9), (S, 0.7), (E, 0.85), (Q, 1.0), (E, 0.8), (E, 0.7), (Q, 0.9)], [(TQ, 1.0), (TQ, 0.85), (TQ, 0.8), (Q, 0.9), (Q, 0.85)]],
    5: [[(S, 1.0), (S, 0.7), (S, 0.75), (S, 0.7), (E, 0.9), (E, 0.8), (S, 0.85), (S, 0.7), (E, 0.8), (Q, 0.9)], [(E, 1.0), (S, 0.7), (S, 0.75), (TQ, 0.9), (TQ, 0.85), (TQ, 0.8), (E, 0.85), (E, 0.7)], [(S, 0.9), (S, 0.7), (S, 0.75), (S, 0.7), (S, 0.85), (S, 0.7), (S, 0.8), (S, 0.7), (Q, 1.0), (Q, 0.9)]],
}

FEEL = {
    'happy':{'staccato':0.3, 'vel_b':10}, 'sad':{'staccato':0.0, 'vel_b':-10},
    'energetic':{'staccato':0.6, 'vel_b':15}, 'calm':{'staccato':0.0, 'vel_b':-15},
    'dark':{'staccato':0.2, 'vel_b':5}, 'epic':{'staccato':0.1, 'vel_b':20},
    'dreamy':{'staccato':0.0, 'vel_b':-5}
}

def get_pats(comp: int, bars: int = 1):
    lvl = max(1, min(5, comp))
    return [random.choice(PATS[lvl]) for _ in range(bars)]

def h_vel(v: int, amt: float = 0.1):
    j = int(v * amt * (random.random() * 2 - 1))
    return max(1, min(127, v + j))

def h_time(d: int, amt: float = 0.02):
    j = random.randint(-int(TPB * amt), int(TPB * amt))
    return max(1, d + j)

def apply_feel(v: int, d: int, mood: str):
    f = FEEL.get(mood, FEEL['happy'])
    v = max(1, min(127, v + f['vel_b']))
    if f.get('staccato', 0) > 0 and random.random() < f['staccato']: d = int(d * 0.6)
    return v, max(1, d)

def chord_rhy(comp: int, bars: int = 1):
    if comp <= 2: return [W] * bars
    res = []
    for _ in range(bars):
        if comp <= 3: res.extend([H, H])
        else: res.extend([H, H] if random.random() < 0.4 else [Q] * 4)
    return res
