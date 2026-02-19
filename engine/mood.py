# Mood parameters for music generation.

MOODS = {
    'happy': {
        'tempo': (110, 140), 'vel': 95, 'v_var': 0.12,
        'pb_ivs': [0, 2, 4, 5, 7], 'bias': 0.55, 'dens': 0.7,
        'octs': (4, 6), 'leap': 0.15, 'arp': 'up'
    },
    'sad': {
        'tempo': (60, 85), 'vel': 70, 'v_var': 0.08,
        'pb_ivs': [0, 1, 2, 3, 5], 'bias': 0.38, 'dens': 0.55,
        'octs': (3, 5), 'leap': 0.08, 'arp': 'down'
    },
    'energetic': {
        'tempo': (130, 170), 'vel': 110, 'v_var': 0.18,
        'pb_ivs': [0, 2, 4, 7], 'bias': 0.52, 'dens': 0.9,
        'octs': (4, 6), 'leap': 0.25, 'arp': 'updown'
    },
    'calm': {
        'tempo': (55, 80), 'vel': 60, 'v_var': 0.06,
        'pb_ivs': [0, 2, 4, 7], 'bias': 0.50, 'dens': 0.45,
        'octs': (3, 5), 'leap': 0.05, 'arp': 'up'
    },
    'dark': {
        'tempo': (70, 100), 'vel': 85, 'v_var': 0.15,
        'pb_ivs': [0, 1, 3, 6], 'bias': 0.40, 'dens': 0.6,
        'octs': (2, 4), 'leap': 0.2, 'arp': 'down'
    },
    'epic': {
        'tempo': (90, 130), 'vel': 105, 'v_var': 0.2,
        'pb_ivs': [0, 4, 5, 7], 'bias': 0.6, 'dens': 0.8,
        'octs': (3, 6), 'leap': 0.3, 'arp': 'updown'
    },
    'dreamy': {
        'tempo': (65, 95), 'vel': 65, 'v_var': 0.1,
        'pb_ivs': [0, 2, 4, 5, 7], 'bias': 0.5, 'dens': 0.5,
        'octs': (4, 6), 'leap': 0.12, 'arp': 'random'
    }
}

def get_mood(m: str):
    return MOODS.get(m, MOODS['happy']).copy()

def get_tempo(m: str):
    p = get_mood(m)
    return sum(p['tempo']) // 2
