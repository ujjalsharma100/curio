from flask import Flask
from flask_cors import CORS
from chat_routes import chat_bp

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Register blueprint
app.register_blueprint(chat_bp)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8087, debug=True)
