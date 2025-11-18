from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# --- App Configuration ---
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
with app.app_context():
    db.create_all()


# --- Database Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# --- Authentication Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return "Username already exists!"

        new_user = User(username=username, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials!"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))

# --- Analysis Routes (Stubs) ---
@app.route('/analyze/youtube/comments', methods=['POST'])
def analyze_youtube_comments():
    text = request.form['text']
    result = "Positive"  # Placeholder for ML model
    return jsonify({'sentiment': result})

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/analyze/instagram/reels', methods=['POST'])
def analyze_instagram_reels():
    caption = request.form['caption']
    comments = request.form['comments']
    result = "Neutral"  # Placeholder for ML pipeline
    return jsonify({'sentiment': result})

# --- Run the App ---
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)