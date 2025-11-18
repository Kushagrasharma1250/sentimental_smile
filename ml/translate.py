from transformers import pipeline
from langdetect import detect

# Load multilingual-to-English translation model
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en")

def translate_to_english(text):
    try:
        if detect(text) != 'en':
            translated = translator(text[:512])[0]['translation_text']
            return translated
        return text
    except Exception as e:
        return f"Translation error: {str(e)}"