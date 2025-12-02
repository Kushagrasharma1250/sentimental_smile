from transformers import pipeline
from ml.translate import translate_to_english

# Lazy-load sentiment model to avoid startup delays and errors
sentiment_pipeline = None

def _get_sentiment_pipeline():
    global sentiment_pipeline
    if sentiment_pipeline is None:
        try:
            sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
        except Exception as e:
            raise Exception(f"Error loading RoBERTa sentiment model: {e}")
    return sentiment_pipeline

def run_text_sentiment(text):
    try:
        if not text or len(text.strip()) == 0:
            return "No text to analyze"
        
        # Check if text is an error message from translation
        if isinstance(text, str) and text.startswith("Translation error"):
            return "Unable to process text"
        
        translated = translate_to_english(text)
        
        # Check if translation failed
        if isinstance(translated, str) and translated.startswith("Translation"):
            return "Unable to process text"
        
        # Ensure translated text is not empty
        if not translated or len(str(translated).strip()) == 0:
            return "No text to analyze"
        
        # Get the sentiment pipeline (lazy-load on first use)
        sentiment = _get_sentiment_pipeline()
        
        # Split into chunks if text is too long
        max_length = 512
        translated_str = str(translated)
        
        if len(translated_str) > max_length:
            # Analyze multiple chunks and average the results
            chunks = [translated_str[i:i+max_length] for i in range(0, len(translated_str), max_length)]
            results = []
            for chunk in chunks:
                if chunk.strip():  # Only analyze non-empty chunks
                    result = sentiment(chunk)[0]
                    results.append(result)
            
            if not results:
                return "Unable to analyze text"
            
            # Calculate average score (raw values from pipeline may already be probabilities in [0,1])
            avg_score = sum(r['score'] for r in results) / len(results)
            # Get majority label
            label = max(set([r['label'] for r in results]), key=[r['label'] for r in results].count)
            # Normalize to percent and cap at 100
            score = _to_percent(avg_score)
        else:
            result = sentiment(translated_str)[0]
            label = result['label']
            # Normalize to percent and cap at 100
            score = _to_percent(result['score'])
        
        # Normalize label to uppercase for consistency
        label_upper = label.upper()
        return f"{label_upper} ({score}%)"
    except Exception as e:
        import traceback
        return f"Error: {str(e)}"


def _to_percent(raw_score):
    """Convert a raw score to a percent in 0..100.

    Handles three common cases:
    - raw_score in [0,1]: treat as probability and multiply by 100
    - raw_score in (1,100]: assume it's already a percentage
    - raw_score > 100 or invalid: cap to 100

    This prevents display of values like 600% due to double-scaling or bad inputs.
    """
    try:
        val = float(raw_score)
    except Exception:
        return 0.0

    if val <= 1.0:
        percent = round(val * 100.0, 2)
    elif val <= 100.0:
        percent = round(val, 2)
    else:
        percent = 100.0

    # Final safety cap
    if percent < 0:
        percent = 0.0
    if percent > 100.0:
        percent = 100.0
    return percent