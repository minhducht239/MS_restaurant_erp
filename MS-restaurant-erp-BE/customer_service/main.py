from flask import Flask, jsonify
from flask_cors import CORS
from routes.customers import bp
from database import db

app = Flask(__name__)
CORS(app)
app.register_blueprint(bp)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db.command('ping')
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


def init_indexes():
    """Initialize indexes on startup"""
    try:
        from create_indexes import create_indexes
        create_indexes()
    except Exception as e:
        print(f"Warning: Could not create indexes: {str(e)}")

if __name__ == "__main__":
    init_indexes()
    app.run(host="0.0.0.0", port=8004)