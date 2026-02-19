# Flask app for Isai MIDI Generator.
import os, time, random
from flask import Flask, render_template, request, jsonify, send_file
from core.scales import NOTES, INTERVALS
from engine.mood import MOODS, get_tempo
from engine.arrangement import arrange
from engine.melody import gen_mel, get_matrix_data
from midi_export import arr_to_midi

app = Flask(__name__)
TDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_midi')
os.makedirs(TDIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html', notes=NOTES, scales=list(INTERVALS.keys()), moods=list(MOODS.keys()))

@app.route('/api/suggest-tempo', methods=['POST'])
def suggest():
    d = request.json or {}
    return jsonify({'tempo': get_tempo(d.get('mood', 'happy'))})

@app.route('/api/matrix', methods=['POST'])
def matrix():
    d = request.json or {}
    mx, labels = get_matrix_data(d.get('root','C'), d.get('scale','major'), d.get('mood','happy'))
    return jsonify({'matrix': mx, 'labels': labels})

@app.route('/api/generate', methods=['POST'])
def gen():
    d = request.json or {}
    r, st, m = d.get('root','C'), d.get('scale','major'), d.get('mood','happy')
    comp, t, bars, s = int(d.get('complexity',3)), d.get('tempo'), int(d.get('bars',16)), d.get('seed')
    if s is None: s = int(time.time() * 1000) % (2**31)
    if r not in NOTES or st not in INTERVALS or m not in MOODS:
        return jsonify({'error': 'Invalid params'}), 400
    arr = arrange(r, st, m, max(1,min(5,comp)), max(4,min(64,bars)), int(t) if t else None, int(s))
    # also get a trace from a single melody call for visualization
    _, trace = gen_mel(r, st, m, comp, min(bars, 8), s)
    fname = f"{r}_{st}_{m}_c{comp}_{s}.mid"
    path = os.path.join(TDIR, fname)
    arr_to_midi(arr, path)
    return jsonify({
        'filename': fname, 'tempo': arr['tempo'],
        'sections': [{'name': x[0], 'bars': x[1]} for x in arr['sections']],
        'stats': {k: len(v) for k, v in arr['tracks'].items()},
        'trace': trace[:40], 'seed': s
    })

@app.route('/api/download/<filename>')
def dl(filename):
    p = os.path.join(TDIR, filename)
    if not os.path.exists(p): return jsonify({'error': 'Not found'}), 404
    return send_file(p, as_attachment=True, download_name=filename, mimetype='audio/midi')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
