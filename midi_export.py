# MIDI export using mido.
import mido
from core.rhythm import TPB

PROGS = {'melody': 0, 'chords': 4, 'bass': 32}
CHANS = {'melody': 0, 'chords': 1, 'bass': 2}

def to_tr(evs: list[dict], name: str, ch: int = 0, pr: int = 0):
    tr = mido.MidiTrack()
    tr.append(mido.MetaMessage('track_name', name=name, time=0))
    tr.append(mido.Message('program_change', program=pr, channel=ch, time=0))
    msgs = []
    for e in evs:
        n, v, t1 = max(0, min(127, e['note'])), max(1, min(127, e['velocity'])), e['time']
        msgs.append(('note_on', n, v, ch, t1))
        msgs.append(('note_off', n, 0, ch, t1 + e['duration']))
    msgs.sort(key=lambda m: (m[4], 0 if m[0] == 'note_off' else 1))
    pt = 0
    for mt, n, v, c, t in msgs:
        d = max(0, t - pt)
        tr.append(mido.Message(mt, note=n, velocity=v, channel=c, time=d))
        pt = t
    return tr

def arr_to_midi(arr: dict, path: str):
    mid = mido.MidiFile(ticks_per_beat=TPB)
    ttr = mido.MidiTrack()
    ttr.append(mido.MetaMessage('track_name', name='Tempo', time=0))
    ttr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(arr['tempo']), time=0))
    ttr.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, time=0))
    t_bar = TPB * 4
    for i, (name, cnt) in enumerate(arr.get('sections', [])):
        ttr.append(mido.MetaMessage('marker', text=name.capitalize(), time=0))
    mid.tracks.append(ttr)
    for name, evs in arr['tracks'].items():
        if not evs: continue
        mid.tracks.append(to_tr(evs, name.capitalize(), CHANS.get(name, 0), PROGS.get(name, 0)))
    mid.save(path)
    return path
