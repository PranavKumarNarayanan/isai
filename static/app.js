/**
 * Isai — App JavaScript
 * Handles UI interactions, API calls, and dynamic rendering.
 */

// ── Scale Data (matches backend) ──
const SCALE_INTERVALS = {
    major: [0, 2, 4, 5, 7, 9, 11],
    minor: [0, 2, 3, 5, 7, 8, 10],
    dorian: [0, 2, 3, 5, 7, 9, 10],
    mixolydian: [0, 2, 4, 5, 7, 9, 10],
    lydian: [0, 2, 4, 6, 7, 9, 11],
    phrygian: [0, 1, 3, 5, 7, 8, 10],
    pentatonic_major: [0, 2, 4, 7, 9],
    pentatonic_minor: [0, 3, 5, 7, 10],
    blues: [0, 3, 5, 6, 7, 10],
    harmonic_minor: [0, 2, 3, 5, 7, 8, 11],
    whole_tone: [0, 2, 4, 6, 8, 10],
};

const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const BLACK_KEYS = new Set([1, 3, 6, 8, 10]); // semitone indices of black keys

// ── DOM Elements ──
const rootSelect = document.getElementById('root-select');
const scaleSelect = document.getElementById('scale-select');
const moodGrid = document.getElementById('mood-grid');
const complexitySlider = document.getElementById('complexity-slider');
const complexityValue = document.getElementById('complexity-value');
const tempoSlider = document.getElementById('tempo-slider');
const tempoValue = document.getElementById('tempo-value');
const barsSlider = document.getElementById('bars-slider');
const barsValue = document.getElementById('bars-value');
const seedInput = document.getElementById('seed-input');
const randomizeSeed = document.getElementById('randomize-seed');
const generateBtn = document.getElementById('generate-btn');
const pianoStrip = document.getElementById('piano-strip');
const emptyState = document.getElementById('empty-state');
const resultCard = document.getElementById('result-card');
const resultTitle = document.getElementById('result-title');
const resultMeta = document.getElementById('result-meta');
const sectionBars = document.getElementById('section-bars');
const resultStats = document.getElementById('result-stats');
const downloadBtn = document.getElementById('download-btn');
const historyList = document.getElementById('history-list');

let currentMood = 'happy';
let currentFilename = null;
let history = [];

// ── Piano Strip Rendering ──
function renderPianoStrip() {
    const root = rootSelect.value;
    const scale = scaleSelect.value;
    const rootIdx = NOTE_NAMES.indexOf(root);
    const intervals = SCALE_INTERVALS[scale];

    // Compute scale notes as semitone offsets from C
    const scaleNotes = new Set(intervals.map(i => (rootIdx + i) % 12));

    pianoStrip.innerHTML = '';

    for (let i = 0; i < 12; i++) {
        const key = document.createElement('div');
        key.className = 'piano-key';

        if (BLACK_KEYS.has(i)) {
            key.classList.add('black');
        } else {
            key.classList.add('white');
        }

        if (i === rootIdx) {
            key.classList.add('root-note');
        } else if (scaleNotes.has(i)) {
            key.classList.add('in-scale');
        }

        key.title = NOTE_NAMES[i];
        pianoStrip.appendChild(key);
    }
}

// ── Mood Selection ──
function setMood(mood) {
    currentMood = mood;
    document.querySelectorAll('.mood-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.mood === mood);
    });
    // Auto-suggest tempo
    fetchSuggestedTempo(mood);
}

async function fetchSuggestedTempo(mood) {
    try {
        const res = await fetch('/api/suggest-tempo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mood }),
        });
        const data = await res.json();
        tempoSlider.value = data.tempo;
        tempoValue.textContent = data.tempo;
    } catch (e) {
        console.warn('Failed to fetch suggested tempo:', e);
    }
}

// ── Slider Updates ──
complexitySlider.addEventListener('input', () => {
    complexityValue.textContent = complexitySlider.value;
});

tempoSlider.addEventListener('input', () => {
    tempoValue.textContent = tempoSlider.value;
});

barsSlider.addEventListener('input', () => {
    barsValue.textContent = barsSlider.value;
});

// ── Seed Randomize ──
randomizeSeed.addEventListener('click', () => {
    seedInput.value = Math.floor(Math.random() * 2147483647);
});

// ── Mood Button Events ──
document.querySelectorAll('.mood-btn').forEach(btn => {
    btn.addEventListener('click', () => setMood(btn.dataset.mood));
});

// ── Scale & Root Change ──
rootSelect.addEventListener('change', renderPianoStrip);
scaleSelect.addEventListener('change', renderPianoStrip);

// ── Generate ──
generateBtn.addEventListener('click', generateMidi);

async function generateMidi() {
    generateBtn.classList.add('loading');

    const payload = {
        root: rootSelect.value,
        scale: scaleSelect.value,
        mood: currentMood,
        complexity: parseInt(complexitySlider.value),
        tempo: parseInt(tempoSlider.value),
        bars: parseInt(barsSlider.value),
    };

    if (seedInput.value) {
        payload.seed = parseInt(seedInput.value);
    }

    try {
        const res = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error || 'Generation failed');
        }

        const data = await res.json();
        showResult(data, payload);
    } catch (e) {
        console.error('Generation error:', e);
        alert('Generation failed: ' + e.message);
    } finally {
        generateBtn.classList.remove('loading');
    }
}

// ── Show Result ──
function showResult(data, config) {
    emptyState.classList.add('hidden');
    resultCard.classList.remove('hidden');

    currentFilename = data.filename;

    // Title
    const scaleLabel = config.scale.replace(/_/g, ' ');
    resultTitle.textContent = `${config.root} ${scaleLabel} — ${config.mood}`;

    // Meta tags
    resultMeta.innerHTML = `
        <span class="meta-tag"><span class="tag-label">Key</span> ${config.root}</span>
        <span class="meta-tag"><span class="tag-label">Scale</span> ${scaleLabel}</span>
        <span class="meta-tag"><span class="tag-label">Mood</span> ${config.mood}</span>
        <span class="meta-tag"><span class="tag-label">BPM</span> ${data.tempo}</span>
        <span class="meta-tag"><span class="tag-label">Complexity</span> ${config.complexity}</span>
        <span class="meta-tag"><span class="tag-label">Seed</span> ${data.seed}</span>
    `;

    // Section bars
    const totalBars = data.sections.reduce((s, sec) => s + sec.bars, 0);
    sectionBars.innerHTML = data.sections.map(sec => {
        const widthPct = (sec.bars / totalBars * 100).toFixed(1);
        return `<div class="section-block ${sec.name}" style="flex: ${sec.bars}" title="${sec.name} (${sec.bars} bars)">${sec.name}</div>`;
    }).join('');

    // Stats
    resultStats.innerHTML = `
        <div class="stat-item">
            <div class="stat-value">${data.stats.melody_notes}</div>
            <div class="stat-label">Melody Notes</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${data.stats.chord_events}</div>
            <div class="stat-label">Chord Events</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">${data.stats.bass_events}</div>
            <div class="stat-label">Bass Events</div>
        </div>
    `;

    // Add to history
    addToHistory(data, config);

    // Scroll result into view
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Download ──
downloadBtn.addEventListener('click', () => {
    if (currentFilename) {
        window.location.href = `/api/download/${currentFilename}`;
    }
});

// ── History ──
function addToHistory(data, config) {
    const entry = {
        filename: data.filename,
        label: `${config.root} ${config.scale.replace(/_/g, ' ')} — ${config.mood} (c${config.complexity})`,
        tempo: data.tempo,
    };

    history.unshift(entry);
    if (history.length > 10) history.pop();
    renderHistory();
}

function renderHistory() {
    if (history.length === 0) {
        historyList.innerHTML = '<p style="color: var(--text-muted); font-size: 0.8rem;">No generations yet.</p>';
        return;
    }

    historyList.innerHTML = history.map(entry => `
        <div class="history-item">
            <div class="history-item-info">
                <span>🎵</span>
                <span>${entry.label}</span>
                <span style="color: var(--text-muted);">${entry.tempo} BPM</span>
            </div>
            <a class="download-link" href="/api/download/${entry.filename}" title="Download">⬇️</a>
        </div>
    `).join('');
}

// ── Init ──
renderPianoStrip();
renderHistory();
fetchSuggestedTempo(currentMood);
