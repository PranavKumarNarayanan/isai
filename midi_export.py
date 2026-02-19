"""
MIDI export: converts internal note events to a standard MIDI file using mido.
"""
import mido
from core.rhythm import TICKS_PER_BEAT


# General MIDI program numbers for track presets
TRACK_PROGRAMS = {
    'melody': 0,    # Acoustic Grand Piano
    'chords': 4,    # Electric Piano 1
    'bass':   32,   # Acoustic Bass
}

TRACK_CHANNELS = {
    'melody': 0,
    'chords': 1,
    'bass':   2,
}


def events_to_midi_track(events: list[dict], track_name: str,
                         channel: int = 0, program: int = 0) -> mido.MidiTrack:
    """
    Convert a list of note events to a mido MidiTrack.

    Each event: {'note': int, 'velocity': int, 'duration': int, 'time': int}
    'time' is absolute ticks from the start.
    """
    track = mido.MidiTrack()
    track.append(mido.MetaMessage('track_name', name=track_name, time=0))
    track.append(mido.Message('program_change', program=program,
                               channel=channel, time=0))

    # Build a list of on/off messages with absolute times
    messages = []
    for evt in events:
        note = max(0, min(127, evt['note']))
        vel = max(1, min(127, evt['velocity']))
        t_on = evt['time']
        t_off = t_on + evt['duration']

        messages.append(('note_on', note, vel, channel, t_on))
        messages.append(('note_off', note, 0, channel, t_off))

    # Sort by absolute time, with note_off before note_on at same time
    messages.sort(key=lambda m: (m[4], 0 if m[0] == 'note_off' else 1))

    # Convert to delta times
    prev_time = 0
    for msg_type, note, vel, ch, abs_time in messages:
        delta = abs_time - prev_time
        delta = max(0, delta)
        track.append(mido.Message(msg_type, note=note, velocity=vel,
                                   channel=ch, time=delta))
        prev_time = abs_time

    return track


def arrangement_to_midi(arrangement: dict, output_path: str) -> str:
    """
    Convert an arrangement dict to a MIDI file.

    Args:
        arrangement: output from engine.arrangement.arrange()
        output_path: file path to write the .mid file

    Returns:
        The output file path.
    """
    mid = mido.MidiFile(ticks_per_beat=TICKS_PER_BEAT)

    # Tempo track
    tempo_track = mido.MidiTrack()
    tempo_track.append(mido.MetaMessage('track_name', name='Tempo', time=0))
    tempo_track.append(mido.MetaMessage('set_tempo',
                                         tempo=mido.bpm2tempo(arrangement['tempo']),
                                         time=0))
    # Time signature: 4/4
    tempo_track.append(mido.MetaMessage('time_signature',
                                         numerator=4, denominator=4,
                                         clocks_per_click=24,
                                         notated_32nd_notes_per_beat=8,
                                         time=0))

    # Key signature from meta
    meta = arrangement.get('meta', {})
    root = meta.get('root', 'C')
    scale = meta.get('scale', 'major')

    # Add section markers
    ticks_per_bar = TICKS_PER_BEAT * 4
    bar_pos = 0
    for section_name, section_bars in arrangement.get('sections', []):
        abs_tick = bar_pos * ticks_per_bar
        delta = abs_tick if bar_pos == 0 else abs_tick  # we'll fix to delta below
        tempo_track.append(mido.MetaMessage('marker',
                                             text=section_name.capitalize(),
                                             time=0))
        bar_pos += section_bars

    mid.tracks.append(tempo_track)

    # Instrument tracks
    for track_name, events in arrangement['tracks'].items():
        if not events:
            continue
        program = TRACK_PROGRAMS.get(track_name, 0)
        channel = TRACK_CHANNELS.get(track_name, 0)
        track = events_to_midi_track(events, track_name.capitalize(),
                                      channel=channel, program=program)
        mid.tracks.append(track)

    mid.save(output_path)
    return output_path
