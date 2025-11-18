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

def detect_content_type(url):
    """Detect if the URL is for an image, reel, or story"""
    if '/reel/' in url or '/reels/' in url:
        return 'reel'
    elif '/stories/' in url:
        return 'story'
    else:
        return 'image'

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

def analyze_instagram_image(url):
    """Analyze Instagram image caption"""
    try:
        shortcode = extract_shortcode(url)
        if not shortcode:
            return "Invalid Instagram image link"

        caption = fetch_caption(shortcode)
        if not caption:
            return "Unable to fetch image caption"

        sentiment = run_text_sentiment(caption)
        return f"Image Caption Sentiment: {sentiment}"
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def analyze_instagram_reel(url):
    """Analyze Instagram reel caption"""
    try:
        shortcode = extract_shortcode(url)
        if not shortcode:
            return "Invalid Instagram reel link"

        caption = fetch_caption(shortcode)
        if not caption:
            return "Unable to fetch reel caption"

        sentiment = run_text_sentiment(caption)
        return f"Reel Caption Sentiment: {sentiment}"
    except Exception as e:
        return f"Error analyzing reel: {str(e)}"

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
        return f"Comments Sentiment: {sentiment}"
    except Exception as e:
        return f"Error analyzing comments: {str(e)}"

def analyze_instagram(url, analysis_type="caption"):
    """Analyze Instagram based on type: 'image', 'reel', 'comments', or 'caption' (default)"""
    content_type = detect_content_type(url)
    
    if analysis_type == 'image' or (analysis_type == 'caption' and content_type == 'image'):
        return analyze_instagram_image(url)
    elif analysis_type == 'reel' or (analysis_type == 'caption' and content_type == 'reel'):
        return analyze_instagram_reel(url)
    elif analysis_type == 'comments':
        return analyze_instagram_comments(url)
    else:
        # Default: analyze based on content type
        if content_type == 'reel':
            return analyze_instagram_reel(url)
        else:
            return analyze_instagram_image(url)