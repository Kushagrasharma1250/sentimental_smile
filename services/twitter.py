import os
import requests
from urllib.parse import urlparse
from ml.text_sentiment import run_text_sentiment

TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAOj75QEAAAAAspFfxZAWgs1mANKFafQX8BJ%2FelY%3DPdV1lc4dafTTQd7311RuMLHcv4nJCRSLdwf2bPt52BKrdUfiAi"

def extract_tweet_id(url):
    try:
        path = urlparse(url).path
        tweet_id = path.split('/')[-1]
        return tweet_id
    except Exception:
        return None

def fetch_tweet_text(tweet_id):
    try:
        headers = {
            "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
        }
        url = f"https://api.twitter.com/2/tweets/{tweet_id}?tweet.fields=text"
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'text' in data['data']:
                return data['data']['text']
        else:
            # Log API error for debugging
            print(f"Twitter API error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception fetching tweet: {str(e)}")
    return None

def analyze_twitter(url):
    try:
        tweet_id = extract_tweet_id(url)
        if not tweet_id:
            return "Invalid Twitter link"

        text = fetch_tweet_text(tweet_id)
        if not text:
            # If API fails, try with a test message to verify sentiment works
            # This helps diagnose whether the issue is API vs. sentiment model
            print(f"Twitter API failed for {tweet_id}, attempting with test text")
            test_text = "This is a great product I really love it"
            sentiment = run_text_sentiment(test_text)
            return f"Tweet: [TEST] {sentiment}"

        sentiment = run_text_sentiment(text)
        if isinstance(sentiment, dict):
            return sentiment
        return {"summary": f"Tweet: {sentiment}"}
    except Exception as e:
        import traceback
        return f"Error analyzing tweet: {str(e)}"