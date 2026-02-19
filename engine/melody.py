# Melody generation via Markov chain on scale degrees.
import random
from core.scales import get_scale
from core.rhythm import get_pats, h_vel, h_time, apply_feel, S
from engine.mood import get_mood

def _build_matrix(n_deg: int, p: dict):
    """Build transition probability matrix for n scale degrees, shaped by mood."""
    mx = [[0.0]*n_deg for _ in range(n_deg)]
    for i in range(n_deg):
        for j in range(n_deg):
            step = abs(i - j)
            if step == 0: w = 0.5
            elif step == 1: w = 5.0      # stepwise: highest weight
            elif step == 2: w = 3.0
            elif step <= 4: w = 1.0 * p['leap']
            else: w = 0.3 * p['leap']
            # direction bias
            if j > i: w *= p['bias'] * 2
            elif j < i: w *= (1 - p['bias']) * 2
            mx[i][j] = max(w, 0.01)
        # normalize row
        total = sum(mx[i])
        mx[i] = [w / total for w in mx[i]]
    return mx

def _step(mx: list, cur: int):
    """Take one Markov step."""
    return random.choices(range(len(mx[cur])), weights=mx[cur], k=1)[0]

def get_motif(mx, l=4, start=0):
    res = [start]
    for _ in range(l - 1): res.append(_step(mx, res[-1]))
    return res

def dev_motif(motif, n, meth='transpose'):
    if meth == 'transpose':
        sh = random.choice([2, 3, -2, -3])
        return [max(0, min(n-1, i+sh)) for i in motif]
    if meth == 'invert':
        piv = motif[0]
        return [max(0, min(n-1, piv-(i-piv))) for i in motif]
    if meth == 'reverse': return list(reversed(motif))
    if meth == 'vary':
        return [max(0, min(n-1, i+random.choice([-1,0,1]))) for i in motif]
    return motif

def gen_mel(root, type, mood, comp, bars=8, s=None):
    if s is not None: random.seed(s)
    p = get_mood(mood)
    scale = get_scale(root, type, p['octs'][0], p['octs'][1])
    if not scale: return [], []
    comp = max(1, min(5, comp))
    n_deg = len(scale)
    mx = _build_matrix(n_deg, p)
    rbars = get_pats(comp, bars)

    # start near middle of range
    target = 12 * ((p['octs'][0] + p['octs'][1]) // 2 + 1)
    start = min(range(n_deg), key=lambda i: abs(scale[i] - target))
    motif = get_motif(mx, 4, start)
    meths = ['transpose', 'invert', 'reverse', 'vary']
    evs, trace, cur, t, m_cnt = [], [], motif[0], 0, 0

    for i, rb in enumerate(rbars):
        if i % 4 == 0 and i > 0: am = dev_motif(motif, n_deg, meths[m_cnt % 4]); m_cnt += 1
        elif i % 2 == 0: am = list(motif)
        else: am = None
        m_pos = 0
        for dur, v_f in rb:
            if random.random() > p['dens']: t += dur; continue
            prev = cur
            if am and m_pos < len(am): cur = am[m_pos]; m_pos += 1
            else: cur = _step(mx, cur)
            note = scale[cur]
            v = h_vel(int(p['vel'] * v_f), p['v_var'])
            v, ndur = apply_feel(v, dur, mood)
            # record transition for visualization
            trace.append({'from': prev, 'to': cur, 'from_note': scale[prev], 'to_note': note, 'prob': round(mx[prev][cur], 3)})
            if comp >= 4 and random.random() < 0.2:
                g = max(0, min(n_deg-1, cur + random.choice([-1,1])))
                evs.append({'note': scale[g], 'velocity': max(1, v-15), 'duration': S, 'time': t})
                t += S; ndur = max(S, ndur-S)
            evs.append({'note': note, 'velocity': v, 'duration': h_time(ndur, 0.015), 'time': t})
            t += dur
    return evs, trace

def get_matrix_data(root, type, mood):
    """Return the transition matrix and scale note names for visualization."""
    p = get_mood(mood)
    scale = get_scale(root, type, p['octs'][0], p['octs'][1])
    if not scale: return [], []
    mx = _build_matrix(len(scale), p)
    from core.scales import NOTES
    labels = [f"{NOTES[n % 12]}{(n//12)-1}" for n in scale]
    # only return a subset for display (one octave worth)
    ivs_count = len(__import__('core.scales', fromlist=['INTERVALS']).INTERVALS[type])
    sub_n = min(ivs_count, len(scale))
    sub_mx = [row[:sub_n] for row in mx[:sub_n]]
    sub_labels = labels[:sub_n]
    return sub_mx, sub_labels
