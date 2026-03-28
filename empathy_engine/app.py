from flask import Flask, render_template, request
from emotion import detect_emotion
from tts_engine import synthesize, EMOTION_CONFIG, get_emotion_emoji

app = Flask(__name__)

MAPPING_TABLE = [
    {
        "emotion": emotion,
        "emoji":   get_emotion_emoji(emotion),
        "rate":    config[0],
        "volume":  config[1],
        "pitch":   config[2],
        "note":    config[3],
    }
    for emotion, config in EMOTION_CONFIG.items()
]

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/synthesize', methods=['POST'])
def synthesize_route():
    text = request.form.get('text', '').strip()

    if not text:
        return render_template('index.html', error="Please enter some text.")

    emotion, intensity = detect_emotion(text)
    params = synthesize(text, emotion, intensity)

    return render_template('index.html',
        text    = text,
        mapping = MAPPING_TABLE,
        result  = {
            "emotion":    emotion,
            "intensity":  intensity,
            "emoji":      params["emoji"],
            "note":       params["note"],
            "rate":       params["rate"],
            "volume":     params["volume"],
            "pitch":      params["pitch"],
            "audio_file": params["audio_file"],
            "audio_type": params["audio_type"],
        }
    )

if __name__ == '__main__':
    print("\n Empathy Engine running")
    app.run(debug=True, port=5000)
