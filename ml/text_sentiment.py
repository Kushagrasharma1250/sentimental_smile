from transformers import pipeline
from ml.translate import translate_to_english

from transformers import pipeline
from ml.translate import translate_to_english

# Use RoBERTa sentiment analysis model for better accuracy
try:
    sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
except Exception as e:
    print(f"Error loading RoBERTa sentiment model: {e}")
    sentiment_pipeline = None

def run_text_sentiment(text):
    try:
        if not text or len(text.strip()) == 0:
            return "No text to analyze"
        
        if sentiment_pipeline is None:
            return "Sentiment analysis model not loaded"
        
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
        
        # Split into chunks if text is too long
        max_length = 512
        translated_str = str(translated)
        
        if len(translated_str) > max_length:
            # Analyze multiple chunks and average the results
            chunks = [translated_str[i:i+max_length] for i in range(0, len(translated_str), max_length)]
            results = []
            for chunk in chunks:
                if chunk.strip():  # Only analyze non-empty chunks
                    result = sentiment_pipeline(chunk)[0]
                    results.append(result)
            
            if not results:
                return "Unable to analyze text"
            
            # Calculate average score
            avg_score = sum(r['score'] for r in results) / len(results)
            # Get majority label
            label = max(set([r['label'] for r in results]), key=[r['label'] for r in results].count)
            score = round(avg_score * 100, 2)
        else:
            result = sentiment_pipeline(translated_str)[0]
            label = result['label']
            score = round(result['score'] * 100, 2)
        
        # Normalize label to uppercase for consistency
        label_upper = label.upper()
        return f"{label_upper} ({score}%)"
    except Exception as e:
        import traceback
        return f"Error: {str(e)}"