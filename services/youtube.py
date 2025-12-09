import os
from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
from ml.text_sentiment import run_text_sentiment

YOUTUBE_API_KEY = "AIzaSyD4pMAKWDzb5qAu2L4anvwysavnTqJ7GRk"

def extract_video_id(url):
    parsed = urlparse(url)
    if 'youtu.be' in parsed.netloc:
        return parsed.path[1:]  
    query = parse_qs(parsed.query)
    return query.get('v', [None])[0]

def fetch_top_comments(video_id, max_comments=20):
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

def analyze_youtube_comments(url):
    """Analyze YouTube comments"""
    try:
        video_id = extract_video_id(url)
        if not video_id:
            return "Invalid YouTube link"

        comments = fetch_top_comments(video_id)
        
        if not comments:
            return "Unable to fetch comments"

        sentiment_result = run_text_sentiment(comments)
        # If sentiment_result is already structured, return it directly
        if isinstance(sentiment_result, dict):
            return sentiment_result
        # Otherwise wrap into a summary dict for compatibility
        return {"summary": f"YouTube Comments: {sentiment_result}"}
    except Exception as e:
        return f"Error analyzing YouTube comments: {str(e)}"