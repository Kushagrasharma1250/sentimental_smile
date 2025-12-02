from transformers import pipeline
from langdetect import detect

# Lazy-load translator to avoid startup delays and errors
translator = None

def _get_translator():
    global translator
    if translator is None:
        try:
            translator = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en")
        except Exception as e:
            raise Exception(f"Failed to load translation model: {str(e)}")
    return translator

def translate_to_english(text):
    try:
        lang = detect(text)
        if lang != 'en':
            trans = _get_translator()
            translated = trans(text[:512])[0]['translation_text']
            return translated
        return text
    except Exception as e:
        # Raise exception instead of returning error string
        raise Exception(f"Translation failed: {str(e)}")