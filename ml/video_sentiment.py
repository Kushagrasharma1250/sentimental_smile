from youtube_transcript_api import YouTubeTranscriptApi
from ml.translate import translate_to_english
from ml.text_sentiment import run_text_sentiment
import cv2
import numpy as np
from deepface import DeepFace
import requests

def analyze_youtube_text(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'hi'])
        text = " ".join([t['text'] for t in transcript])
        translated = translate_to_english(text)
        return run_text_sentiment(translated)
    except Exception as e:
        return f"Transcript not available: {str(e)}"
    
def analyze_youtube_visual(video_id):
    try:
        # Fetch default thumbnail
        url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
        resp = requests.get(url)
        img_array = np.asarray(bytearray(resp.content), dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        return result[0]['dominant_emotion']
    except Exception as e:
        return f"Visual sentiment not available: {str(e)}"
def analyze_video_sentiment(video_id):
    text_result = analyze_youtube_text(video_id)
    image_result = analyze_youtube_visual(video_id)

    return {
        "platform": "YouTube Video",
        "text_sentiment": text_result,
        "visual_sentiment": image_result,
        "combined_summary": f"Text: {text_result}, Visual: {image_result}"
    }