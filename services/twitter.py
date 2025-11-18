import os
import requests
from urllib.parse import urlparse
from ml.text_sentiment import run_text_sentiment

TWITTER_BEARER_TOKEN = os.environ.get("AAAAAAAAAAAAAAAAAAAAAOj75QEAAAAAspFfxZAWgs1mANKFafQX8BJ%2FelY%3DPdV1lc4dafTTQd7311RuMLHcv4nJCRSLdwf2bPt52BKrdUfiAi")

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
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()['data']['text']
    except Exception:
        pass
    return None

def analyze_twitter(url):
    tweet_id = extract_tweet_id(url)
    if not tweet_id:
        return "Invalid Twitter link"

    text = fetch_tweet_text(tweet_id)
    if not text:
        return "Unable to fetch tweet"

    sentiment = run_text_sentiment(text)
    return f"Tweet Sentiment: {sentiment}"