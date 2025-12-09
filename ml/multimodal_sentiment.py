"""
Multimodal sentiment analysis for YouTube videos.
Analyzes video frames and transcribed audio without downloading the full video.
"""

import os
import subprocess
import tempfile
import json
from io import BytesIO

try:
    from PIL import Image
    import numpy as np
    import torch
    from transformers import pipeline, CLIPProcessor, CLIPModel
    import yt_dlp
except ImportError as e:
    raise ImportError(f"Required packages missing. Install: yt-dlp transformers pillow torch. Error: {e}")

from ml.text_sentiment import run_text_sentiment

# Lazy-load models
clip_model = None
clip_processor = None
transcription_pipeline = None

def _get_clip_model():
    """Lazy-load CLIP model for visual sentiment analysis"""
    global clip_model, clip_processor
    if clip_model is None:
        try:
            clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        except Exception as e:
            raise Exception(f"Error loading CLIP model: {e}")
    return clip_model, clip_processor

def _get_transcription_pipeline():
    """Lazy-load Whisper for audio transcription"""
    global transcription_pipeline
    if transcription_pipeline is None:
        try:
            transcription_pipeline = pipeline("automatic-speech-recognition", 
                                             model="openai/whisper-base")
        except Exception as e:
            raise Exception(f"Error loading Whisper model: {e}")
    return transcription_pipeline

def extract_video_frames(youtube_url, max_frames=5, frame_interval=10):
    """
    Extract frames from YouTube video without downloading the full file.
    
    Args:
        youtube_url: YouTube video URL
        max_frames: Maximum frames to extract
        frame_interval: Interval in seconds between frames
    
    Returns:
        List of PIL Image objects
    """
    try:
        ydl_opts = {
            'format': 'best[height<=360]/worst',  # Low resolution to save bandwidth
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            video_url = info['url']
        
        # Use ffmpeg to extract frames at intervals
        frames = []
        with tempfile.TemporaryDirectory() as tmpdir:
            frame_pattern = os.path.join(tmpdir, 'frame_%d.jpg')
            
            cmd = [
                'ffmpeg',
                '-i', video_url,
                '-vf', f'fps=1/{frame_interval}',
                '-vframes', str(max_frames),
                frame_pattern,
                '-loglevel', 'error'
            ]
            
            subprocess.run(cmd, check=False, capture_output=True)
            
            # Load extracted frames
            for i in range(1, max_frames + 1):
                frame_file = os.path.join(tmpdir, f'frame_{i}.jpg')
                if os.path.exists(frame_file):
                    frames.append(Image.open(frame_file).convert('RGB'))
        
        return frames if frames else None
    except Exception as e:
        raise Exception(f"Error extracting video frames: {e}")

def extract_audio_transcript(youtube_url):
    """
    Extract and transcribe audio from YouTube video.
    
    Args:
        youtube_url: YouTube video URL
    
    Returns:
        Transcribed text
    """
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 30,
            'outtmpl': os.path.join(tempfile.gettempdir(), 'audio_%(id)s'),
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            audio_file = ydl.prepare_filename(info).replace('.webm', '.wav').replace('.mp4', '.wav')
        
        if not os.path.exists(audio_file):
            # Fallback: try common output format
            base_path = os.path.join(tempfile.gettempdir(), f"audio_{info['id']}.wav")
            if os.path.exists(base_path):
                audio_file = base_path
            else:
                return None
        
        # Transcribe audio
        transcriber = _get_transcription_pipeline()
        result = transcriber(audio_file)
        
        # Clean up
        try:
            os.remove(audio_file)
        except:
            pass
        
        return result.get('text', '') if result else None
    except Exception as e:
        raise Exception(f"Error extracting/transcribing audio: {e}")

def analyze_visual_sentiment(frames):
    """
    Analyze visual sentiment of video frames using CLIP.
    
    Args:
        frames: List of PIL Image objects
    
    Returns:
        Dict with visual sentiment scores
    """
    if not frames:
        return {"error": "No frames available"}
    
    try:
        model, processor = _get_clip_model()
        
        # Sentiment-related prompts for visual analysis
        prompts = [
            "a happy and positive scene",
            "a sad and negative scene",
            "a neutral scene",
            "bright and cheerful",
            "dark and gloomy",
            "calm and peaceful"
        ]
        
        text_inputs = processor(text=prompts, return_tensors="pt", padding=True)
        
        visual_scores = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
        
        for frame in frames:
            image_inputs = processor(images=frame, return_tensors="pt")
            
            with torch.no_grad():
                image_features = model.get_image_features(**image_inputs)
                text_features = model.get_text_features(**text_inputs)
                
                # Normalize features
                image_features /= image_features.norm(dim=-1, keepdim=True)
                text_features /= text_features.norm(dim=-1, keepdim=True)
                
                # Compute similarity scores
                similarities = (image_features @ text_features.T).squeeze()
        
        # Map prompt similarities to sentiment categories
        visual_scores["positive"] = float((similarities[0] + similarities[3]).mean() * 50)  # happy + bright
        visual_scores["negative"] = float((similarities[1] + similarities[4]).mean() * 50)  # sad + dark
        visual_scores["neutral"] = float(similarities[2].mean() * 50)  # neutral
        
        # Normalize to 0-100
        total = visual_scores["positive"] + visual_scores["negative"] + visual_scores["neutral"]
        if total > 0:
            for key in visual_scores:
                visual_scores[key] = min(100, visual_scores[key] * 100 / total)
        
        return visual_scores
    except Exception as e:
        return {"error": str(e)}

def analyze_youtube_multimodal(youtube_url):
    """
    Perform multimodal sentiment analysis on a YouTube video.
    Analyzes video frames and audio transcription only.
    
    Args:
        youtube_url: YouTube video URL
    
    Returns:
        Dict with combined sentiment scores and analysis details
    """
    try:
        results = {
            "url": youtube_url,
            "components": {},
            "error": None
        }
        
        # 1. Extract and analyze video frames
        try:
            frames = extract_video_frames(youtube_url, max_frames=5, frame_interval=15)
            if frames:
                visual_sentiment = analyze_visual_sentiment(frames)
                results["components"]["visual"] = visual_sentiment
        except Exception as e:
            results["components"]["visual"] = {"error": str(e)}
        
        # 2. Extract and transcribe audio
        try:
            transcript = extract_audio_transcript(youtube_url)
            if transcript:
                audio_sentiment = run_text_sentiment(transcript)
                if isinstance(audio_sentiment, dict):
                    results["components"]["audio_text"] = audio_sentiment
                else:
                    results["components"]["audio_text"] = {"summary": audio_sentiment}
        except Exception as e:
            results["components"]["audio_text"] = {"error": str(e)}
        
        # 3. Combine all sentiments
        combined = {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
        component_count = 0
        
        for component_name, component_result in results["components"].items():
            if isinstance(component_result, dict) and "error" not in component_result:
                for key in ["positive", "negative", "neutral"]:
                    if key in component_result:
                        combined[key] += component_result[key]
                component_count += 1
        
        # Average across components
        if component_count > 0:
            for key in combined:
                combined[key] /= component_count
        
        # Determine top label
        top_label = max(combined.keys(), key=lambda k: combined.get(k, 0.0))
        top_confidence = min(100, combined.get(top_label, 0.0))
        
        results.update({
            "positive": combined["positive"],
            "negative": combined["negative"],
            "neutral": combined["neutral"],
            "label": top_label.upper(),
            "confidence": top_confidence,
            "summary": f"{top_label.upper()} ({top_confidence:.1f}%)"
        })
        
        return results
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "summary": f"Multimodal analysis failed: {str(e)}"
        }