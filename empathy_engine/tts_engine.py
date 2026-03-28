import os
import subprocess

EMOTION_CONFIG = {
    #             rate   volume  pitch   note
    "joy":       (210,   90,     10,    "fast, loud, high pitch"),
    "surprise":  (200,   85,     8,     "fast, high pitch, animated"),
    "anger":     (185,   100,   -10,    "fast, loud, low pitch, forceful"),
    "fear":      (195,   60,     5,     "fast, quiet, mid-high pitch, tense"),
    "neutral":   (155,   75,     0,     "normal speed, normal pitch"),
    "disgust":   (120,   65,    -12,    "slow, low pitch, flat tone"),
    "sadness":   (100,   55,    -15,    "slow, quiet, very low pitch"),
}

EMOTION_EMOJI = {
    "joy": "😄", "surprise": "😲", "anger": "😠",
    "fear": "😨", "neutral": "😐", "disgust": "🤢", "sadness": "😢"
}

VOICE_PITCH_MAP = {
    "high": ["Samantha", "Victoria", "Karen"],
    "mid":  ["Alex",     "Daniel",   "Tom"],
    "low":  ["Fred",     "Ralph",    "Bruce"],
}

def get_emotion_emoji(emotion: str) -> str:
    return EMOTION_EMOJI.get(emotion, "🎙️")

def get_vocal_params(emotion: str, intensity: float) -> dict:
    base_rate, base_vol, base_pitch, note = EMOTION_CONFIG.get(
        emotion, EMOTION_CONFIG["neutral"]
    )

    # Intensity scaling 
    scale = (intensity - 0.75) * 2

    final_rate  = int(max(80,  min(250, base_rate + (scale * 20))))
    final_vol   = int(max(40,  min(100, base_vol  + (scale * 10))))
    final_pitch = int(max(-50, min(50,  base_pitch + (scale * 5))))

    # Pick voice based on pitch target
    if final_pitch >= 5:
        voice = VOICE_PITCH_MAP["high"][0]
    elif final_pitch <= -5:
        voice = VOICE_PITCH_MAP["low"][0]
    else:
        voice = VOICE_PITCH_MAP["mid"][0]

    return {
        "rate":    final_rate,
        "volume":  final_vol,
        "pitch":   final_pitch,
        "voice":   voice,
        "note":    note,
        "emoji":   get_emotion_emoji(emotion),
        "intensity": intensity
    }

def synthesize(text: str, emotion: str, intensity: float) -> dict:
    base_dir   = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, "static")
    os.makedirs(static_dir, exist_ok=True)

    aiff_path = os.path.join(static_dir, "output.aiff")
    mp3_path  = os.path.join(static_dir, "output.mp3")

    # Clean old files
    for f in [aiff_path, mp3_path]:
        if os.path.exists(f):
            os.remove(f)

    params = get_vocal_params(emotion, intensity)

    print(f"\n{'─'*45}")
    print(f"  VOCAL PARAMETERS APPLIED")
    print(f"{'─'*45}")
    print(f"  Emotion  : {emotion.upper()} ({intensity})")
    print(f"  Rate     : {params['rate']} wpm")
    print(f"  Volume   : {params['volume']} / 100")
    print(f"  Pitch    : {params['pitch']} semitones")
    print(f"  Voice    : {params['voice']}")
    print(f"  Style    : {params['note']}")
    print(f"{'─'*45}")

    # 1: Mac say command 
    try:
        cmd = [
            "say",
            "-v", params["voice"],   # voice (controls pitch)
            "-r", str(params["rate"]),  # rate (speed)
            "-o", aiff_path,         # output file
            "--data-format=LEF32@22050",  # good quality format
            text
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if os.path.exists(aiff_path) and os.path.getsize(aiff_path) > 1000:
            print(f" say command succeeded → {aiff_path}")
            params["audio_file"] = "output.aiff"
            params["audio_type"] = "audio/aiff"
            return params
        else:
            print(f"  say failed: {result.stderr}")

    except Exception as e:
        print(f"  say error: {e}")

    # 2: gTTS fallback 
    try:
        print("  Trying gTTS fallback...")
        from gtts import gTTS
        slow = params["rate"] < 140
        tts = gTTS(text=text, lang='en', slow=slow)
        tts.save(mp3_path)

        if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1000:
            print(f" gTTS fallback succeeded → {mp3_path}")
            params["audio_file"] = "output.mp3"
            params["audio_type"] = "audio/mpeg"
            return params

    except Exception as e:
        print(f" gTTS failed: {e}")

    params["audio_file"] = None
    params["audio_type"] = None
    return params
