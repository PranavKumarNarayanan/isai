const IVS = {
    major: [0, 2, 4, 5, 7, 9, 11], minor: [0, 2, 3, 5, 7, 8, 10], dorian: [0, 2, 3, 5, 7, 9, 10],
    mixolydian: [0, 2, 4, 5, 7, 9, 10], lydian: [0, 2, 4, 6, 7, 9, 11], phrygian: [0, 1, 3, 5, 7, 8, 10],
    pentatonic_major: [0, 2, 4, 7, 9], pentatonic_minor: [0, 3, 5, 7, 10], blues: [0, 3, 5, 6, 7, 10],
    harmonic_minor: [0, 2, 3, 5, 7, 8, 11], whole_tone: [0, 2, 4, 6, 8, 10]
};
const NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'], BLACKS = new Set([1, 3, 6, 8, 10]);
const $ = id => document.getElementById(id);
const rSel = $('root-select'), sSel = $('scale-select'), compS = $('complexity-slider'), compV = $('complexity-value');
const tempS = $('tempo-slider'), tempV = $('tempo-value'), barsS = $('bars-slider'), barsV = $('bars-value');
const seedI = $('seed-input'), btnG = $('generate-btn'), rCard = $('result-card'), rMeta = $('result-meta');
const sBars = $('section-bars'), rStats = $('result-stats'), btnD = $('download-btn'), hList = $('history-list');
const mxViz = $('markov-viz'), mxCon = $('matrix-container'), trList = $('trace-list'), pStrip = $('piano-strip');

let mood = 'happy', fname = null, history = [];

function renderP() {
    const r = rSel.value, ri = NOTES.indexOf(r), ivs = IVS[sSel.value], sn = new Set(ivs.map(i => (ri + i) % 12));
    pStrip.innerHTML = '';
    for (let i = 0; i < 12; i++) {
        let k = document.createElement('div'); k.className = 'piano-key ' + (BLACKS.has(i) ? 'black' : 'white');
        if (i === ri) k.classList.add('root-note'); else if (sn.has(i)) k.classList.add('in-scale');
        pStrip.appendChild(k);
    }
}

function setM(m) {
    mood = m; document.querySelectorAll('.mood-btn').forEach(b => b.classList.toggle('active', b.dataset.mood === m));
    fetch('/api/suggest-tempo', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ mood: m }) })
        .then(r => r.json()).then(d => { tempS.value = d.tempo; tempV.textContent = d.tempo; });
}

compS.oninput = () => compV.textContent = compS.value;
tempS.oninput = () => tempV.textContent = tempS.value;
barsS.oninput = () => barsV.textContent = barsS.value;
$('randomize-seed').onclick = () => seedI.value = Math.floor(Math.random() * 2147483647);
document.querySelectorAll('.mood-btn').forEach(b => b.onclick = () => setM(b.dataset.mood));
rSel.onchange = sSel.onchange = renderP;

btnG.onclick = async () => {
    btnG.classList.add('loading'); btnG.textContent = 'Generating...';
    let p = { root: rSel.value, scale: sSel.value, mood, complexity: parseInt(compS.value), tempo: parseInt(tempS.value), bars: parseInt(barsS.value) };
    if (seedI.value) p.seed = parseInt(seedI.value);
    try {
        let r = await fetch('/api/generate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(p) });
        if (!r.ok) throw new Error('Failed');
        let d = await r.json(); showR(d, p);
        // fetch transition matrix for viz
        let mr = await fetch('/api/matrix', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(p) });
        let md = await mr.json(); showMatrix(md.matrix, md.labels, d.trace);
    } catch (e) { alert(e.message) } finally { btnG.classList.remove('loading'); btnG.textContent = 'Generate MIDI'; }
};

function showR(d, c) {
    rCard.classList.remove('hidden'); fname = d.filename;
    rMeta.innerHTML = [`Key: ${c.root}`, `Scale: ${c.scale}`, `Mood: ${c.mood}`, `BPM: ${d.tempo}`, `Seed: ${d.seed}`].map(t => `<span class="meta-tag">${t}</span>`).join('');
    let tb = d.sections.reduce((s, x) => s + x.bars, 0);
    sBars.innerHTML = d.sections.map(x => `<div class="section-block" style="flex:${x.bars}">${x.name} (${x.bars})</div>`).join('');
    rStats.innerHTML = Object.entries(d.stats).map(([k, v]) => `<span>${k}: <b>${v}</b></span>`).join('');
    history.unshift({ f: d.filename, l: `${c.root} ${c.scale} ${c.mood}`, t: d.tempo });
    if (history.length > 10) history.pop(); renderH();
    rCard.scrollIntoView({ behavior: 'smooth' });
}

function renderH() {
    hList.innerHTML = history.length ? history.map(x => `<div class="history-item"><span>${x.l} (${x.t} BPM)</span><a href="/api/download/${x.f}">⬇</a></div>`).join('') : '<p style="color:#999;font-size:0.8rem">No generations yet.</p>';
}

function showMatrix(mx, labels, trace) {
    mxViz.classList.remove('hidden');
    if (!mx.length) { mxCon.innerHTML = '<p>No data</p>'; return; }
    // build table
    let h = '<table class="mx-grid"><tr><th></th>' + labels.map(l => `<th>${l}</th>`).join('') + '</tr>';
    for (let i = 0; i < mx.length; i++) {
        h += '<tr><th>' + labels[i] + '</th>';
        for (let j = 0; j < mx[i].length; j++) {
            let v = mx[i][j], bg = `rgba(0,0,0,${Math.min(v * 3, 0.9).toFixed(2)})`, fg = v * 3 > 0.5 ? '#fff' : '#000';
            h += `<td style="background:${bg};color:${fg}">${v.toFixed(2)}</td>`;
        }
        h += '</tr>';
    }
    h += '</table>';
    mxCon.innerHTML = h;
    // trace
    if (!trace || !trace.length) { trList.innerHTML = '<p>No trace data</p>'; return; }
    trList.innerHTML = trace.map((t, i) => `<div class="trace-step"><span>#${i + 1}</span> <span class="from">${NOTES[t.from_note % 12]}${Math.floor(t.from_note / 12) - 1}</span> <span class="arrow">→</span> <span class="to">${NOTES[t.to_note % 12]}${Math.floor(t.to_note / 12) - 1}</span> <span class="prob">(p=${t.prob})</span></div>`).join('');
}

btnD.onclick = () => fname && (location.href = `/api/download/${fname}`);
renderP(); renderH(); setM(mood);
