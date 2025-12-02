import os
from transformers import pipeline
from ml.translate import translate_to_english

# Suppress TensorFlow logging to reduce noise
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

_sentiment_pipeline = None

def _get_sentiment_pipeline():
    """
    Lazy-loads the sentiment analysis pipeline to avoid loading it on startup.
    """
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        _sentiment_pipeline = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')
    return _sentiment_pipeline

def run_text_sentiment(text):
    """
    Analyzes the sentiment of the given text.
    """
    try:
        if not text or not text.strip():
            return "No text to analyze"

        translated = translate_to_english(text)
        if isinstance(translated, str) and translated.startswith("Translation error"):
            return "Could not process text due to translation failure"

        if not translated or not str(translated).strip():
            return "No text to analyze after translation"

        sentiment_pipeline = _get_sentiment_pipeline()
        result = sentiment_pipeline(str(translated))

        if result:
            label = result[0]['label']
            score = result[0]['score'] * 100
            return f"{label.upper()} ({score:.2f}%)"
        
        return "Sentiment not determined"

    except Exception as e:
        return f"An error occurred during text sentiment analysis: {str(e)}"
