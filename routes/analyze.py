from flask import Blueprint, request, render_template, session, redirect
from services.youtube import analyze_youtube_comments, analyze_youtube_multimodal_full
from services.twitter import analyze_twitter
from services.instagram import analyze_instagram_comments

analyze_bp = Blueprint('analyze_bp', __name__)

@analyze_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@analyze_bp.route('/analyze/youtube', methods=['POST'])
def analyze_youtube_route():
    if 'user_id' not in session:
        return redirect('/login')

    link = request.form['link']
    sentiment = analyze_youtube_comments(link)

    return render_template('dashboard.html', sentiment=sentiment, platform='youtube')

@analyze_bp.route('/analyze/youtube/multimodal', methods=['POST'])
def analyze_youtube_multimodal_route():
    """Multimodal analysis: video frames + audio + comments"""
    if 'user_id' not in session:
        return redirect('/login')

    link = request.form['link']
    sentiment = analyze_youtube_multimodal_full(link)

    return render_template('dashboard.html', sentiment=sentiment, platform='youtube_multimodal')

@analyze_bp.route('/analyze/twitter', methods=['POST'])
def analyze_twitter_route():
    if 'user_id' not in session:
        return redirect('/login')

    link = request.form['link']
    sentiment = analyze_twitter(link)

    return render_template('dashboard.html', sentiment=sentiment, platform='twitter')

@analyze_bp.route('/analyze/instagram', methods=['POST'])
def analyze_instagram_route():
    if 'user_id' not in session:
        return redirect('/login')

    link = request.form['link']
    sentiment = analyze_instagram_comments(link)

    return render_template('dashboard.html', sentiment=sentiment, platform='instagram')

@analyze_bp.route('/analyze', methods=['POST'])
def analyze():
    """Legacy route that auto-detects platform and analyzes comments"""
    if 'user_id' not in session:
        return redirect('/login')

    link = request.form['link']
    sentiment = "Unsupported link"

    if 'youtube.com' in link or 'youtu.be' in link:
        sentiment = analyze_youtube_comments(link)
    elif 'twitter.com' in link:
        sentiment = analyze_twitter(link)
    elif 'instagram.com' in link:
        sentiment = analyze_instagram_comments(link)

    return render_template('dashboard.html', sentiment=sentiment)