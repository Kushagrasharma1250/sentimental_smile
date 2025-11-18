from flask import Blueprint, request, render_template, session, redirect
from services.youtube import analyze_youtube
from services.twitter import analyze_twitter
from services.instagram import analyze_instagram

analyze_bp = Blueprint('analyze_bp', __name__)

@analyze_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

@analyze_bp.route('/analyze', methods=['POST'])
def analyze():
    if 'user_id' not in session:
        return redirect('/login')

    link = request.form['link']
    sentiment = "Unsupported link"

    if 'youtube.com' in link or 'youtu.be' in link:
        sentiment = analyze_youtube(link)
    elif 'twitter.com' in link:
        sentiment = analyze_twitter(link)
    elif 'instagram.com' in link:
        sentiment = analyze_instagram(link)

    return render_template('dashboard.html', sentiment=sentiment)