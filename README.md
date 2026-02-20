# Isai

A procedural MIDI generator that composes multi-track music using Markov chains. 

You pick a root note, scale, and mood. The program builds a transition probability matrix for the scale degrees, then walks through it note by note to produce melodies. Chords and bass lines are generated separately using progression templates. The output is a standard `.mid` file you can open in any DAW.

## What is a markov chain

A Markov chain is a system where the next state depends only on the current state, not on anything that happened before. In our case, each "state" is a note in the scale.

Say you're on note E in a C major scale. The Markov chain has a row of probabilities for E that says things like:

```
from E:
  -> F  (one step up)    probability: 0.31
  -> D  (one step down)  probability: 0.28
  -> G  (a third up)     probability: 0.14
  -> C  (a third down)   probability: 0.12
  -> E  (stay)           probability: 0.03
  -> A  (a fourth up)    probability: 0.07
  -> B  (a fifth up)     probability: 0.05
```

The numbers in each row always add up to 1. To pick the next note, we roll a weighted random number using these probabilities. Stepwise motion (moving to an adjacent note) gets the highest weight, which is why melodies sound coherent instead of random.

The interesting part is that the matrix isn't hardcoded — it's constructed at runtime based on the mood you select. Each mood has parameters that reshape the matrix:

- **Direction bias**: a "happy" mood biases the matrix toward ascending intervals (bias = 0.55), while "sad" biases toward descending (bias = 0.38)
- **Leap probability**: "epic" allows large interval jumps (0.3), while "calm" keeps things close (0.05)
- **Note density**: controls how many rhythm slots actually get a note vs. a rest

So the same scale produces different-sounding melodies depending on mood, because the transition probabilities are different.

## How it works here.

1. **User Configuration**: root note (C-B), scale (major, minor, dorian, blues, etc.), mood (happy, sad, dark, epic, etc.), complexity (1-5), tempo, duration in bars

2. **Matrix construction** (`engine/melody.py → _build_matrix`):
   - creates an N×N matrix where N = number of notes in the scale across the selected octave range
   - for each cell (i, j): assigns a weight based on the interval distance between note i and note j
   - step of 1 gets weight 5.0, step of 2 gets 3.0, larger intervals get scaled by the mood's leap probability
   - multiplies by direction bias (ascending vs descending preference)
   - multiplies by octave range preference (notes in the mood's comfortable octave get 2x weight)
   - normalizes each row so it sums to 1.0

3. **Melody generation** (`engine/melody.py → gen_mel`):
   - picks a starting note near the center of the comfortable octave range
   - generates a 4-note motif using the chain
   - walks through each bar's rhythm pattern:
     - if it's a motif bar, plays the motif (or a developed version — transposed, inverted, reversed, or varied)
     - otherwise, takes a Markov step from the current note
     - applies humanization: slight velocity and timing jitter
     - at complexity 4+, occasionally inserts grace notes
   - records every transition (from-note, to-note, probability) for the visualization

4. **Chord generation** (`core/chords.py`):
   - picks a progression template based on mood (e.g., happy defaults to I-V-vi-IV patterns)
   - builds chords from scale degree roots with appropriate qualities (major, minor, diminished)
   - at higher complexity, substitutes some chords (e.g., maj → maj7, min → sus4)

5. **Bass generation** (`engine/arrangement.py → _bass`):
   - follows the chord roots, dropped to bass octave
   - at complexity 3+, splits into walking bass patterns

6. **Arrangement** (`engine/arrangement.py → arrange`):
   - picks a song structure based on total bars (short: intro-verse-chorus-outro, medium and long variants)
   - distributes bars across sections
   - each section has an energy level (chorus = 1.0, outro = 0.5) that scales velocity and complexity
   - generates melody/chords/bass per section and stitches them together

7. **MIDI export** (`midi_export.py`):
   - converts the internal event list to mido messages
   - melody on channel 0 (piano), chords on channel 1 (electric piano), bass on channel 2 (acoustic bass)
   - writes a standard type-1 MIDI file


## setup

You need python 3.10+ and pip.

### Windows

```powershell
cd path\to\isai
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

if you get a script execution policy error on the Activate line, run this first:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux

```bash
cd path/to/isai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

if `python3 -m venv` fails on debian/ubuntu, you may need:

```bash
sudo apt install python3-venv
```

### MacOS

```bash
cd path/to/isai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

if you don't have python 3.10+, install it via homebrew:

```bash
brew install python@3.12
```

## Usage

### CLI

```bash
python generate.py --root C --scale minor --mood dark --complexity 4 --bars 16
```

All flags:

| flag           | default  | description                          |
|----------------|----------|--------------------------------------|
| `--root`       | C        | root note (C, C#, D, ... B)          |
| `--scale`      | major    | scale type                           |
| `--mood`       | happy    | mood profile                         |
| `--complexity` | 3        | 1-5, affects rhythm density and ornamentation |
| `--tempo`      | auto     | BPM, auto-selected from mood if omitted |
| `--bars`       | 16       | total bars (4-64)                    |
| `--seed`       | random   | for reproducible output              |
| `--output`     | auto     | output filename                      |

available scales: `major`, `minor`, `dorian`, `mixolydian`, `lydian`, `phrygian`, `pentatonic_major`, `pentatonic_minor`, `blues`, `harmonic_minor`, `whole_tone`

available moods: `happy`, `sad`, `energetic`, `calm`, `dark`, `epic`, `dreamy`

### Web UI

```bash
python app.py
```

Ppen `http://localhost:5000` in your browser. Configure settings, hit Generate. the page will show your MIDI file info, a download button, and a visualization of the Markov chain matrix + the transition trace from that specific generation.

## The visualization

after generating, the web ui shows two things:

1. **Transition matrix**: a table where row = current note, column = next note. each cell shows the probability. cells are shaded — darker means higher probability. you can see that adjacent notes (stepwise motion) are always the darkest, which is why the melodies don't sound random.

2. **Transition trace**: the actual sequence of transitions the algorithm took. each line shows `Note A → Note B (p=0.xx)`, so you can follow the chain's walk and see what probabilities it was working with at each step.

## Dependencies

- **mido** — reads and writes standard MIDI files
- **flask** — serves the web ui

both are in `requirements.txt`.

## Seed reproducibility

if you pass `--seed 12345` (or type a seed in the Web UI), you'll get the exact same output every time. This is particularly useful in iterating over the same generation settings.

## Output format

Standard MIDI type 1 file with 3 tracks:

| track   | channel | GM program      |
|---------|---------|-----------------|
| melody  | 0       | 0 (acoustic piano) |
| chords  | 1       | 4 (electric piano)  |
| bass    | 2       | 32 (acoustic bass)  |

480 ticks per beat, 4/4 time. section markers are embedded as MIDI marker events.

## WebUi Demo
![WebUI Demo](assets\webui.gif)
