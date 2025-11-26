from flask import Flask, jsonify, request
from db import init_db
from routes.payments import bp as payments_bp
from utils.logger import logger

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/payment_db"

init_db(app)

@app.before_request
def log_request():
    logger.info({
        "event": "incoming_request",
        "method": request.method,
        "path": request.path,
        "args": request.args.to_dict(),
        "body": request.get_json(silent=True),
        "headers": dict(request.headers)
    })

@app.after_request
def log_response(response):
    logger.info({
        "event": "response_sent",
        "status": response.status_code,
        "path": request.path,
    })
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error({
        "event": "internal_error",
        "error": str(e),
        "path": request.path
    })
    return jsonify({"error": "Internal Server Error"}), 500


app.register_blueprint(payments_bp, url_prefix='/api/payments')

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