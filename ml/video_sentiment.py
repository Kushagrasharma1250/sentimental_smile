from moviepy.editor import VideoFileClip
import whisper
import cv2
from deepface import DeepFace
from ml.text_sentiment import run_text_sentiment
from ml.translate import translate_to_english

def extract_audio(video_path):
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile("temp_audio.wav")

def transcribe_audio():
    model = whisper.load_model("base")
    result = model.transcribe("temp_audio.wav")
    return result['text']

def extract_frames(video_path, interval=30):
    cap = cv2.VideoCapture(video_path)
    frames = []
    i = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if i % interval == 0:
            frames.append(frame)
        i += 1
    cap.release()
    return frames

def analyze_video_sentiment(video_path):
    try:
        extract_audio(video_path)
        transcript = transcribe_audio()
        translated = translate_to_english(transcript)
        text_result = run_text_sentiment(translated)

        frames = extract_frames(video_path)
        emotions = []
        for f in frames:
            try:
                result = DeepFace.analyze(f, actions=['emotion'], enforce_detection=False)
                emotions.append(result[0]['dominant_emotion'])
            except:
                continue

        image_result = max(set(emotions), key=emotions.count) if emotions else "Unknown"
        return f"Text: {text_result}, Visual: {image_result}"
    except Exception as e:
        return f"Error analyzing video sentiment: {str(e)}"