# Song arrangement and structure.
import random
from core.scales import get_scale, INTERVALS, NOTES, name_to_midi
from core.chords import get_prog, arp as arp_fn
from core.rhythm import TPB, W, H, Q, E, chord_rhy, h_vel
from engine.melody import gen_mel
from engine.mood import get_mood

STRUCTS = {
    'short': ['intro', 'verse', 'chorus', 'outro'],
    'medium': ['intro', 'verse', 'chorus', 'verse', 'chorus', 'outro'],
    'long': ['intro', 'verse', 'prechorus', 'chorus', 'verse', 'prechorus', 'chorus', 'bridge', 'chorus', 'outro']
}

ENERGY = {'intro': 0.6, 'verse': 0.75, 'prechorus': 0.85, 'chorus': 1.0, 'bridge': 0.7, 'outro': 0.5}

def _struct(bars: int):
    return STRUCTS['short' if bars <= 12 else 'medium' if bars <= 32 else 'long']

def _div(bars: int, secs: list[str]):
    n = len(secs)
    b = max(2, bars // n)
    rem = bars - b * n
    res = [b] * n
    pri = ['chorus', 'verse', 'bridge', 'prechorus', 'intro', 'outro']
    i = 0
    while rem > 0:
        for idx, name in enumerate(secs):
            if name == pri[i % 6] and rem > 0: res[idx] += 1; rem -= 1
        i += 1
        if i > 100: break
    return res

def _bass(prog: list[list[int]], durs: list[int], mood: str, comp: int):
    p = get_mood(mood)
    evs, t = [], 0
    for ch, d in zip(prog, durs):
        if not ch: t += d; continue
        bn = min(ch)
        while bn > 48: bn -= 12
        v = h_vel(int(p['vel'] * 0.85))
        if comp >= 3 and d >= H:
            stps = 2 if comp < 4 else 4
            sd = d // stps
            for s in range(stps):
                n = bn if s == 0 else bn + random.choice([0, 2, 4, 5, 7])
                while n > 55: n -= 12
                evs.append({'note': n, 'velocity': v, 'duration': int(sd * 0.9), 'time': t})
                t += sd
        else:
            evs.append({'note': bn, 'velocity': v, 'duration': int(d * 0.9), 'time': t})
            t += d
    return evs

def _chords(prog: list[list[int]], durs: list[int], mood: str, comp: int):
    p = get_mood(mood)
    evs, t = [], 0
    for ch, d in zip(prog, durs):
        if not ch: t += d; continue
        v = h_vel(int(p['vel'] * 0.7))
        if comp >= 4:
            anotes = arp_fn(ch, p['arp'], d // E if d >= Q else 2)
            sd = d // len(anotes) if anotes else d
            for n in anotes:
                evs.append({'note': n, 'velocity': h_vel(v), 'duration': int(sd * 0.85), 'time': t})
                t += sd
        else:
            for n in ch: evs.append({'note': n, 'velocity': v, 'duration': int(d * 0.9), 'time': t})
            t += d
    return evs

def arrange(r: str, st: str, m: str, comp: int, bars: int = 16, temp: int = None, s: int = None):
    if s is not None: random.seed(s)
    p = get_mood(m)
    if temp is None: temp = random.randint(*p['tempo'])
    comp, bars = max(1, min(5, comp)), max(4, bars)
    secs = _struct(bars)
    bcnts = _div(bars, secs)
    mevs, cevs, bevs, off_b = [], [], [], 0
    tpb_ = TPB * 4
    for name, blen in zip(secs, bcnts):
        en = ENERGY.get(name, 0.75)
        scomp = max(1, min(5, int(comp * en + 0.5)))
        t_off = off_b * tpb_
        smel, _ = gen_mel(r, st, m, scomp, blen, s + off_b if s else None)
        for e in smel: e['time'] += t_off; e['velocity'] = max(1, min(127, int(e['velocity'] * en)))
        mevs.extend(smel)
        prog = get_prog(m, st, r, 3, scomp, blen)
        durs = chord_rhy(scomp, blen)
        ml = min(len(prog), len(durs))
        prog, durs = prog[:ml], durs[:ml]
        sch = _chords(prog, durs, m, scomp)
        for e in sch: e['time'] += t_off; e['velocity'] = max(1, min(127, int(e['velocity'] * en)))
        cevs.extend(sch)
        sba = _bass(prog, durs, m, scomp)
        for e in sba: e['time'] += t_off; e['velocity'] = max(1, min(127, int(e['velocity'] * en)))
        bevs.extend(sba)
        off_b += blen
    return {
        'tempo': temp,
        'tracks': {'melody': mevs, 'chords': cevs, 'bass': bevs},
        'sections': list(zip(secs, bcnts)),
        'meta': {'root': r, 'scale': st, 'mood': m, 'comp': comp, 'bars': bars, 'tempo': temp}
    }
