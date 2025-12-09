import os
import requests
from urllib.parse import urlparse
from ml.text_sentiment import run_text_sentiment

INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN")

def extract_shortcode(url):
    try:
        path = urlparse(url).path
        parts = path.strip('/').split('/')
        return parts[-1] if parts else None
    except Exception:
        return None

def fetch_comments(shortcode, max_comments=10):
    """Fetch comments from an Instagram post"""
    try:
        media_id = shortcode
        url = f"https://graph.facebook.com/v18.0/{media_id}/comments?fields=text&limit={max_comments}&access_token={INSTAGRAM_ACCESS_TOKEN}"
        response = requests.get(url)
        if response.status_code == 200:
            comments = [item['text'] for item in response.json().get('data', [])]
            return ' '.join(comments) if comments else None
    except Exception:
        pass
    return None

def analyze_instagram_comments(url):
    """Analyze Instagram post comments"""
    try:
        shortcode = extract_shortcode(url)
        if not shortcode:
            return "Invalid Instagram link"

        comments = fetch_comments(shortcode)
        if not comments:
            return "Unable to fetch post comments"

        sentiment = run_text_sentiment(comments)
        if isinstance(sentiment, dict):
            return sentiment
        return {"summary": f"Instagram Comments: {sentiment}"}
    except Exception as e:
        return f"Error analyzing comments: {str(e)}"