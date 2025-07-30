from flask import Flask
from src.api.ingest import ingest_bp
from src.api.summarize import summarize_bp

application = Flask(__name__)
application.register_blueprint(ingest_bp)
application.register_blueprint(summarize_bp)

@application.route('/')
def index():
    return "Hello, World!"

if __name__ == '__main__':
    application.run(debug=True, port=5000)
