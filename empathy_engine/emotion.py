from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=1
)

print("Emotion Model loaded")

def detect_emotion(text: str) -> tuple:
    result = classifier(text)[0][0]
    label = result['label'].lower()
    score = round(result['score'], 3)
    print(f"  → Emotion: {label} | Confidence: {score}")
    return label, score
