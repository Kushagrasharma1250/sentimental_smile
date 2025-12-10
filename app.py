from flask import Flask, request, jsonify
from config import SECRET_KEY, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models.user import db
from routes.auth import auth_bp
from routes.analyze import analyze_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(analyze_bp)

with app.app_context():
    db.create_all()

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    sentiment = "positive" if data['text'].count('good') > data['text'].count('bad') else "negative"
    return jsonify({"sentiment": sentiment})
# © Kushagra Sharma 
if __name__ == '__main__':
    app.run(debug=True)