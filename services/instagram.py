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

def fetch_caption(shortcode):
    try:
        # You need to map shortcode to media ID via unofficial endpoint or saved mapping
        # For simplicity, assume you already have media_id
        media_id = shortcode  # Replace with actual mapping logic

        url = f"https://graph.facebook.com/v18.0/{media_id}?fields=caption&access_token={INSTAGRAM_ACCESS_TOKEN}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('caption', '')
    except Exception:
        pass
    return None

def analyze_instagram(url):
    shortcode = extract_shortcode(url)
    if not shortcode:
        return "Invalid Instagram link"

    caption = fetch_caption(shortcode)
    if not caption:
        return "Unable to fetch caption"

    sentiment = run_text_sentiment(caption)
    return f"Instagram Caption Sentiment: {sentiment}"