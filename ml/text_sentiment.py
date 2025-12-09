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
            return {"error": "No text to analyze"}

        # Check if text is an error message from translation
        if isinstance(text, str) and text.startswith("Translation error"):
            return {"error": "Unable to process text"}

        translated = translate_to_english(text)

        # Check if translation failed
        if isinstance(translated, str) and translated.startswith("Translation"):
            return {"error": "Unable to process text"}

        # Ensure translated text is not empty
        if not translated or len(str(translated).strip()) == 0:
            return {"error": "No text to analyze"}

        # Get the sentiment pipeline (lazy-load on first use)
        sentiment = _get_sentiment_pipeline()

        # Helper to extract a label->score map from pipeline output
        def _scores_map_from_output(output):
            # When `return_all_scores=True` the pipeline returns a list of
            # score dicts for all labels; otherwise it may return a single
            # dict for the top class. Normalize both cases to a map.
            scores = {}
            if isinstance(output, list):
                for item in output:
                    lbl = str(item.get("label", "")).lower()
                    scores[lbl] = float(item.get("score", 0.0))
            elif isinstance(output, dict):
                lbl = str(output.get("label", "")).lower()
                scores[lbl] = float(output.get("score", 0.0))
            return scores

        # We want results for these canonical keys
        label_keys = ["positive", "negative", "neutral"]

        # Split into chunks if text is too long
        max_length = 512
        translated_str = str(translated)

        cumulative = {k: 0.0 for k in label_keys}
        chunk_count = 0

        if len(translated_str) > max_length:
            chunks = [translated_str[i:i+max_length] for i in range(0, len(translated_str), max_length)]
            for chunk in chunks:
                if not chunk.strip():
                    continue
                # request all scores so we can assemble per-label percentages
                out = sentiment(chunk, return_all_scores=True)[0]
                scores = _scores_map_from_output(out)
                for k in label_keys:
                    cumulative[k] += scores.get(k, 0.0)
                chunk_count += 1

            if chunk_count == 0:
                return {"error": "Unable to analyze text"}

            averaged = {k: (cumulative[k] / chunk_count) for k in label_keys}
        else:
            out = sentiment(translated_str, return_all_scores=True)[0]
            scores = _scores_map_from_output(out)
            averaged = {k: scores.get(k, 0.0) for k in label_keys}

        # Convert raw scores to percentages
        percents = {k: _to_percent(averaged.get(k, 0.0)) for k in label_keys}

        # Determine top label and confidence
        top_label = max(averaged.keys(), key=lambda k: averaged.get(k, 0.0))
        top_confidence = percents.get(top_label, 0.0)

        # Build a structured result (keeps a human-readable summary for
        # backward compatibility while returning per-label scores)
        result = {
            "positive": percents["positive"],
            "negative": percents["negative"],
            "neutral": percents["neutral"],
            "label": top_label.upper(),
            "confidence": top_confidence,
            "summary": f"{top_label.upper()} ({top_confidence}%)",
        }

        return result
    except Exception as e:
        return {"error": str(e)}


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