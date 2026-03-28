# Empathy Engine: Giving AI a Human Voice

A Flask web service that detects the emotion in input text and synthesizes speech with vocal parameters — rate, volume, and pitch — dynamically modulated to match that emotion. The result is expressive, human-like audio output that goes beyond monotonic TTS delivery.


## Features

- **7 Granular Emotions** : joy, surprise, anger, fear, neutral, disgust, sadness — powered by a fine-tuned transformer model
- **Intensity Scaling** : the model's confidence score scales how strongly the voice modulates — weak emotion = subtle change, strong emotion = dramatic change
- **Web Interface**: paste text, click Generate, see emotion + vocal parameters + play audio in-browser
- **Fully offline TTS** with macOS `say` fallback to `gTTS`


## Tech Stack

| Layer | Tool |
|---|---|
| Emotion Detection | `j-hartmann/emotion-english-distilroberta-base` (HuggingFace Transformers) |
| Text-to-Speech | macOS `say` command (primary) / `gTTS` (fallback) |
| Web Framework | Flask + Jinja2 |


## Project Structure

```
empathy-engine/
├── app.py              # Flask routes
├── emotion.py          # HuggingFace emotion detection
├── tts_engine.py       # Vocal parameter logic + audio synthesis
├── templates/
│   └── index.html      # Web UI
├── static/             # Generated audio files served from here
├── requirements.txt
└── README.md
```

---

## Setup & Running

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd empathy-engine
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download the emotion model

Run this once before starting the server. It downloads and caches the model (~300 MB) and runs a quick test to confirm everything is working:

```bash
python3 -c "
from transformers import pipeline
print('Downloading model... please wait')
classifier = pipeline(
    'text-classification',
    model='j-hartmann/emotion-english-distilroberta-base',
    top_k=1
)
print('Model downloaded and cached successfully!')
print('Testing model...')
result = classifier('I am so happy today!')
print(f'Test result: {result}')
"
```

You should see output like:
```
Model downloaded and cached successfully!
Testing model...
Test result: [[{'label': 'joy', 'score': 0.9741}]]
```

> The model is cached locally at `~/.cache/huggingface/` after the first download. Subsequent runs load it instantly without re-downloading.

### 5. Run the server
```bash
python app.py
```

### 6. Open in browser
```
http://localhost:5000
```

Type any text, click **Generate Expressive Speech**, and the page will show the detected emotion, vocal parameters applied, and an audio player.

---

## Design Choices

### Emotion Detection

Uses `j-hartmann/emotion-english-distilroberta-base`, a DistilRoBERTa model fine-tuned on multiple emotion datasets. It returns one of 7 emotion labels along with a confidence score (0.0 – 1.0). This was chosen over simpler sentiment libraries (e.g. VADER, TextBlob) because it supports granular multi-class emotion detection rather than a basic positive/negative split.

### Emotion → Voice Parameter Mapping

Each emotion is mapped to a base configuration of three vocal parameters:

| Emotion | Base Rate (wpm) | Base Volume (%) | Base Pitch (semitones) | Style |
|---|---|---|---|---|
| joy | 210 | 90 | +10 | Fast, loud, high pitch |
| surprise | 200 | 85 | +8 | Fast, high pitch, animated |
| anger | 185 | 100 | -10 | Fast, loud, low pitch |
| fear | 195 | 60 | +5 | Fast, quiet, tense |
| neutral | 155 | 75 | 0 | Normal speed and pitch |
| disgust | 120 | 65 | -12 | Slow, low pitch, flat |
| sadness | 100 | 55 | -15 | Slow, quiet, very low pitch |

### Intensity Scaling

The model's confidence score drives how much each parameter deviates from its base value:

```python
scale = (intensity - 0.75) * 2

final_rate  = base_rate  + (scale * 20)
final_vol   = base_vol   + (scale * 10)
final_pitch = base_pitch + (scale * 5)
```

The `0.75` anchor means that at 75% confidence the output stays close to the base values. Above 75%, the vocal effect intensifies; below 75%, it softens. This produces a natural gradient:

| Input Text | Model Output | Scale | Effect |
|---|---|---|---|
| "This is good" | joy @ 0.60 | −0.30 | Slight rate/pitch increase |
| "This is great!" | joy @ 0.80 | +0.10 | Moderate increase |
| "This is the best news ever!!" | joy @ 0.95 | +0.40 | Significant rate and pitch increase |

This directly satisfies the intensity scaling bonus requirement — the same emotion produces a noticeably different voice depending on how strongly the text expresses it.

### Voice Selection (Pitch)

Since `pyttsx3` has limited cross-platform pitch control, the service uses the macOS `say` command with named voices that correspond to different tonal ranges:

| Pitch Target | Voices Used |
|---|---|
| High (pitch ≥ +5) | Samantha, Victoria, Karen |
| Mid | Alex, Daniel, Tom |
| Low (pitch ≤ −5) | Fred, Ralph, Bruce |

On non-macOS systems, `gTTS` is used as a fallback (rate modulation applied via slow/normal flag).

---

## API

### `POST /synthesize`

Form body:

| Field | Type | Description |
|---|---|---|
| `text` | string | The input text to synthesize |

Response: renders `index.html` with detected emotion, intensity score, vocal parameters, and a link to the generated audio file.

---

## Requirements

```
flask
transformers
torch
gtts
```

> macOS users get the best experience as the `say` command supports named voices and fine-grained rate control. On other platforms, `gTTS` handles synthesis automatically.
