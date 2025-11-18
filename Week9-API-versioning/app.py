from flask import Flask, jsonify
from db import init_db
from routes.v1 import bp as v1_bp
from routes.v2 import bp as v2_bp

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/payment_db"

init_db(app)

app.register_blueprint(v1_bp, url_prefix='/api/v1/payments')
app.register_blueprint(v2_bp, url_prefix='/api/v2/payments')

@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to Payment API System",
        "versions": [
            {"version": "v1", "status": "Deprecated", "docs": "/api/v1/payments"},
            {"version": "v2", "status": "Active", "docs": "/api/v2/payments"}
        ]
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)