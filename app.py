"""
Flask web server for Isai — Procedural MIDI Generator.
Serves the web UI and handles generation API requests.
"""
import os
import io
import time
import random
from flask import Flask, render_template, request, jsonify, send_file

from core.scales import NOTE_NAMES, SCALE_INTERVALS
from engine.mood import MOOD_PROFILES, suggest_tempo
from engine.arrangement import arrange
from midi_export import arrangement_to_midi

app = Flask(__name__)

# Directory for temporary MIDI files
TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_midi')
os.makedirs(TEMP_DIR, exist_ok=True)


@app.route('/')
def index():
    """Serve the main UI page."""
    return render_template('index.html',
                           notes=NOTE_NAMES,
                           scales=list(SCALE_INTERVALS.keys()),
                           moods=list(MOOD_PROFILES.keys()))


@app.route('/api/suggest-tempo', methods=['POST'])
def api_suggest_tempo():
    """Return suggested tempo for a mood."""
    data = request.json or {}
    mood = data.get('mood', 'happy')
    return jsonify({'tempo': suggest_tempo(mood)})


@app.route('/api/generate', methods=['POST'])
def api_generate():
    """Generate a MIDI file and return it for download."""
    data = request.json or {}

    root = data.get('root', 'C')
    scale_type = data.get('scale', 'major')
    mood = data.get('mood', 'happy')
    complexity = int(data.get('complexity', 3))
    tempo = data.get('tempo')
    bars = int(data.get('bars', 16))
    seed = data.get('seed')

    if tempo is not None:
        tempo = int(tempo)
    if seed is not None:
        seed = int(seed)
    else:
        seed = int(time.time() * 1000) % (2**31)

    # Validate inputs
    if root not in NOTE_NAMES:
        return jsonify({'error': f'Invalid root note: {root}'}), 400
    if scale_type not in SCALE_INTERVALS:
        return jsonify({'error': f'Invalid scale: {scale_type}'}), 400
    if mood not in MOOD_PROFILES:
        return jsonify({'error': f'Invalid mood: {mood}'}), 400

    complexity = max(1, min(5, complexity))
    bars = max(4, min(64, bars))

    # Generate
    arrangement = arrange(
        root=root,
        scale_type=scale_type,
        mood=mood,
        complexity=complexity,
        total_bars=bars,
        tempo=tempo,
        seed=seed,
    )

    # Export to MIDI
    filename = f"{root}_{scale_type}_{mood}_c{complexity}_{seed}.mid"
    filepath = os.path.join(TEMP_DIR, filename)
    arrangement_to_midi(arrangement, filepath)

    # Return file info
    return jsonify({
        'filename': filename,
        'tempo': arrangement['tempo'],
        'sections': [{'name': s[0], 'bars': s[1]} for s in arrangement['sections']],
        'stats': {
            'melody_notes': len(arrangement['tracks']['melody']),
            'chord_events': len(arrangement['tracks']['chords']),
            'bass_events': len(arrangement['tracks']['bass']),
        },
        'seed': seed,
    })


@app.route('/api/download/<filename>')
def api_download(filename):
    """Download a generated MIDI file."""
    filepath = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    return send_file(filepath, as_attachment=True,
                     download_name=filename,
                     mimetype='audio/midi')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
