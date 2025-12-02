import os
from transformers import pipeline
from ml.translate import translate_to_english

# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

_sentiment_pipeline = None

def _get_sentiment_pipeline():
    """Lazy-loads the sentiment analysis pipeline."""
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        _sentiment_pipeline = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')
    return _sentiment_pipeline

def run_video_sentiment(video_path):
    """
    Analyzes the sentiment of a video's simulated transcription.
    """
    # This is a mock transcription. In a real scenario, you'd extract audio and transcribe it.
    mock_transcription = f"Simulated transcription from video: {video_path}"

    try:
        if not mock_transcription.strip():
            return "No text to analyze"

        translated = translate_to_english(mock_transcription)
        if isinstance(translated, str) and translated.startswith("Translation error"):
            return "Could not process video text due to translation failure"

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
        return f"An error occurred during video sentiment analysis: {str(e)}"
