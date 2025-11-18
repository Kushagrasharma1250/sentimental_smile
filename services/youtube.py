import os
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from ml.text_sentiment import run_text_sentiment

YOUTUBE_API_KEY = os.environ.get("AIzaSyDFbb3NzammiA1dw8FJpobxwlL-cf_6E2I")

def extract_video_id(url):
    parsed = urlparse(url)
    if 'youtu.be' in parsed.netloc:
        return parsed.path[1:]
    query = parse_qs(parsed.query)
    return query.get('v', [None])[0]

def fetch_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript])
    except Exception:
        return None

def fetch_top_comments(video_id, max_comments=10):
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_comments,
            textFormat='plainText'
        ).execute()

        comments = [
            item['snippet']['topLevelComment']['snippet']['textDisplay']
            for item in response.get('items', [])
        ]
        return ' '.join(comments)
    except Exception:
        return None

def analyze_youtube(url):
    video_id = extract_video_id(url)
    if not video_id:
        return "Invalid YouTube link"

    transcript = fetch_transcript(video_id)
    comments = fetch_top_comments(video_id)

    results = []

    if transcript:
        results.append(f"Transcript: {run_text_sentiment(transcript)}")
    if comments:
        results.append(f"Comments: {run_text_sentiment(comments)}")

    return ' | '.join(results) if results else "No analyzable content found"