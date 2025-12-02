import os
<<<<<<< HEAD
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
from ml.translate import translate_to_english
=======
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
from ml.text_sentiment import run_text_sentiment
>>>>>>> parent of a21cfa8 (feat: Implement sentiment analysis with pie charts)

# Suppress TensorFlow logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

<<<<<<< HEAD
_sentiment_pipeline = None
=======
def extract_video_id(url):
    parsed = urlparse(url)
    if 'youtu.be' in parsed.netloc:
        return parsed.path[1:]  
    query = parse_qs(parsed.query)
    return query.get('v', [None])[0]
>>>>>>> parent of a21cfa8 (feat: Implement sentiment analysis with pie charts)

def _get_sentiment_pipeline():
    """Lazy-loads the sentiment analysis pipeline."""
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        _sentiment_pipeline = pipeline(
            'sentiment-analysis',
            model='distilbert-base-uncased-finetuned-sst-2-english'
        )
    return _sentiment_pipeline


def _extract_video_id(video_url: str) -> str:
    """Extracts the YouTube video ID from a URL."""
    if "v=" in video_url:
        return video_url.split("v=")[-1].split("&")[0]
    elif "youtu.be/" in video_url:
        return video_url.split("youtu.be/")[-1].split("?")[0]
    else:
        raise ValueError("Invalid YouTube URL format")

def run_video_sentiment(video_url: str):
    """
    Analyzes the sentiment of a YouTube video's transcript.
    Steps:
    1. Extract video ID
    2. Fetch transcript
    3. Translate to English
    4. Run sentiment analysis
    """
    try:
        video_id = _extract_video_id(video_url)

        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        text = " ".join([t['text'] for t in transcript])
        print("Transcript length:", len(text))
        if not text.strip():
            return "No transcript available for this video"

        translated = translate_to_english(text)
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

<<<<<<< HEAD
    except Exception as e:
        return f"An error occurred during video sentiment analysis: {str(e)}"
=======
        sentiment_result = run_text_sentiment(comments)
        return f"YouTube Comments: {sentiment_result}"
    except Exception as e:
        return f"Error analyzing YouTube comments: {str(e)}"
>>>>>>> parent of a21cfa8 (feat: Implement sentiment analysis with pie charts)
