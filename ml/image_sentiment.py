from transformers import pipeline
from PIL import Image
import requests
from io import BytesIO

# Load image-to-text model (BLIP) to describe images
try:
    image_to_text_pipeline = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
except Exception as e:
    print(f"Error loading image-to-text model: {e}")
    image_to_text_pipeline = None

# Load RoBERTa sentiment analysis model
try:
    sentiment_pipeline = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
except Exception as e:
    print(f"Error loading RoBERTa sentiment model: {e}")
    sentiment_pipeline = None

def load_image_from_url(image_url):
    """Load image from URL"""
    try:
        response = requests.get(image_url, timeout=10)
        image = Image.open(BytesIO(response.content))
        return image
    except Exception as e:
        return None

def load_image_from_path(image_path):
    """Load image from local path"""
    try:
        image = Image.open(image_path)
        return image
    except Exception as e:
        return None

def generate_image_caption(image):
    """Generate caption/description for an image"""
    try:
        if image_to_text_pipeline is None:
            return None
        
        # Convert RGBA to RGB if necessary
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        caption_result = image_to_text_pipeline(image)
        if caption_result and len(caption_result) > 0:
            return caption_result[0]['generated_text']
        return None
    except Exception as e:
        print(f"Error generating image caption: {e}")
        return None

def run_image_sentiment(image_source):
    """
    Analyze sentiment of an image by generating caption and analyzing it
    image_source can be: URL string, file path string, or PIL Image object
    """
    try:
        # Load image based on source type
        if isinstance(image_source, str):
            if image_source.startswith('http'):
                image = load_image_from_url(image_source)
            else:
                image = load_image_from_path(image_source)
        else:
            image = image_source
        
        if image is None:
            return "Unable to load image"
        
        # Generate caption for the image
        caption = generate_image_caption(image)
        if not caption:
            return "Unable to generate image description"
        
        # Analyze sentiment of the caption
        if sentiment_pipeline is None:
            return "Sentiment analysis model not loaded"
        
        result = sentiment_pipeline(caption)[0]
        label = result['label'].upper()
        score = round(result['score'] * 100, 2)
        
        return f"{label} ({score}%)"
    except Exception as e:
        import traceback
        return f"Error analyzing image sentiment: {str(e)}"