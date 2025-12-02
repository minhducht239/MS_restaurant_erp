from flask import Flask, jsonify
from flask_cors import CORS
from routes.tables import bp as tables_bp
from database import db

app = Flask(__name__)
CORS(app)
app.register_blueprint(tables_bp)

@app.route("/")
def root():
    return jsonify({
        "service": "Tables Service",
        "version": "1.0.0",
        "status": "running"
    })

@app.route("/health")
def health():
    try:
        db.command('ping')
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8007)