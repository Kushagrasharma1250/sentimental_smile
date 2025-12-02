from googletrans import Translator

def translate_to_english(text):
    """
    Translates the given text to English using the googletrans library.
    """
    try:
        translator = Translator()
        translation = translator.translate(text, dest='en')
        return translation.text
    except Exception as e:
        return f"Translation error: {str(e)}"
