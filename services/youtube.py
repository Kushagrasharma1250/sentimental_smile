import os
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from ml.text_sentiment import run_text_sentiment

YOUTUBE_API_KEY = "AIzaSyD4pMAKWDzb5qAu2L4anvwysavnTqJ7GRk"

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

def analyze_youtube_video(url):
    """Analyze only the video transcript/content"""
    try:
        video_id = extract_video_id(url)
        if not video_id:
            return "Invalid YouTube link"

        transcript = fetch_transcript(video_id)
        
        if not transcript:
            # Return a default test message to verify sentiment analysis works
            test_text = "This is a great video with amazing content"
            test_result = run_text_sentiment(test_text)
            return f"Video Transcript: [TEST] {test_result}"

        sentiment_result = run_text_sentiment(transcript)
        return f"Video Transcript: {sentiment_result}"
    except Exception as e:
        import traceback
        error_msg = f"Error analyzing YouTube video: {str(e)}\n{traceback.format_exc()}"
        return error_msg

def analyze_youtube_comments(url):
    """Analyze only the video comments"""
    try:
        video_id = extract_video_id(url)
        if not video_id:
            return "Invalid YouTube link"

        comments = fetch_top_comments(video_id)
        
        if not comments:
            return "Unable to fetch video comments"

        sentiment_result = run_text_sentiment(comments)
        return f"Video Comments: {sentiment_result}"
    except Exception as e:
        return f"Error analyzing YouTube comments: {str(e)}"

def analyze_youtube(url, analysis_type="both"):
    """Analyze video based on type: 'video', 'comments', or 'both'"""
    results = []
    
    if analysis_type in ["video", "both"]:
        results.append(analyze_youtube_video(url))
    
    if analysis_type in ["comments", "both"]:
        results.append(analyze_youtube_comments(url))
    
    return ' | '.join(results) if results else "No analyzable content found"