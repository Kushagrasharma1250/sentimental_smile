from transformers import pipeline
from ml.translate import translate_to_english

sentiment_pipeline = pipeline("sentiment-analysis")

def run_text_sentiment(text):
    try:
        translated = translate_to_english(text)
        result = sentiment_pipeline(translated[:512])[0]
        label = result['label']
        score = round(result['score'] * 100, 2)
        return f"{label} ({score}%)"
    except Exception as e:
        return f"Error analyzing text sentiment: {str(e)}"