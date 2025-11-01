from flask import Flask
from flask_cors import CORS
from routes.tables import bp as tables_bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(tables_bp)

@app.route("/")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003)