from transformers import pipeline

# Load sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

def run_text_sentiment(text):
    try:
        # Truncate long text to avoid model input limits
        truncated = text[:512]
        result = sentiment_pipeline(truncated)[0]
        label = result['label']
        score = round(result['score'] * 100, 2)
        return f"{label} ({score}%)"
    except Exception as e:
        return f"Error analyzing text sentiment: {str(e)}"