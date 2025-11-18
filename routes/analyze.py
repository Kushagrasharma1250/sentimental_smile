from flask import Blueprint, request, render_template, session, redirect
from services.youtube import analyze_youtube, analyze_youtube_video, analyze_youtube_comments
from services.twitter import analyze_twitter
from services.instagram import analyze_instagram, analyze_instagram_image, analyze_instagram_reel, analyze_instagram_comments

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
    analysis_type = request.form.get('analysis_type', 'both')
    
    if analysis_type == 'video':
        sentiment = analyze_youtube_video(link)
    elif analysis_type == 'comments':
        sentiment = analyze_youtube_comments(link)
    else:
        sentiment = analyze_youtube(link, 'both')

    return render_template('dashboard.html', sentiment=sentiment, platform='youtube')

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
    analysis_type = request.form.get('analysis_type', 'caption')
    
    if analysis_type == 'image':
        sentiment = analyze_instagram_image(link)
    elif analysis_type == 'reel':
        sentiment = analyze_instagram_reel(link)
    elif analysis_type == 'comments':
        sentiment = analyze_instagram_comments(link)
    else:
        sentiment = analyze_instagram(link, 'caption')

    return render_template('dashboard.html', sentiment=sentiment, platform='instagram')

@analyze_bp.route('/analyze', methods=['POST'])
def analyze():
    """Legacy route that auto-detects platform"""
    if 'user_id' not in session:
        return redirect('/login')

    link = request.form['link']
    analysis_type = request.form.get('analysis_type', 'both')
    sentiment = "Unsupported link"

    if 'youtube.com' in link or 'youtu.be' in link:
        if analysis_type == 'video':
            sentiment = analyze_youtube_video(link)
        elif analysis_type == 'comments':
            sentiment = analyze_youtube_comments(link)
        else:
            sentiment = analyze_youtube(link, 'both')
    elif 'twitter.com' in link:
        sentiment = analyze_twitter(link)
    elif 'instagram.com' in link:
        insta_type = request.form.get('analysis_type', 'caption')
        if insta_type == 'image':
            sentiment = analyze_instagram_image(link)
        elif insta_type == 'reel':
            sentiment = analyze_instagram_reel(link)
        elif insta_type == 'comments':
            sentiment = analyze_instagram_comments(link)
        else:
            sentiment = analyze_instagram(link, 'caption')

    return render_template('dashboard.html', sentiment=sentiment)