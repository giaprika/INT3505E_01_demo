from flask import Flask, jsonify, request
from db import init_db
from routes.payments import bp as payments_bp
from utils.logger import logger
from utils.limiter import limiter
from prometheus_flask_exporter import PrometheusMetrics
from pybreaker import CircuitBreaker, CircuitBreakerError
import random
import time

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/payment_db"

init_db(app)
limiter.init_app(app)

metrics = PrometheusMetrics(app, group_by='endpoint')
metrics.info("app_info", "Payment API Monitoring")

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
    if request.path == '/metrics':
        return e  # trả default handler của Flask / Prometheus
    return jsonify({"error": "Endpoint not found"}), 404



circuit = CircuitBreaker(fail_max=3, reset_timeout=10)

# Hàm giả lập gọi service ngoài
def external_service_call():
    if random.random() > 0.4:
        time.sleep(0.1)
        raise ConnectionError("External Service bị lỗi hoặc quá tải")
    return "Dữ liệu thành công từ Service B"

@app.route('/api/data')
def get_protected_data():
    try:
        result = circuit.call(external_service_call)
        
        return jsonify({
            "status": "Thành công",
            "message": result,
            "breaker_state": circuit.current_state
        }), 200

    except CircuitBreakerError:
        return jsonify({
            "status": "Lỗi",
            "message": "Hệ thống phụ đang bị ngắt mạch (Circuit OPEN).",
            "breaker_state": circuit.current_state,
            "action": "FALLBACK: Trả về dữ liệu mặc định hoặc Cache"
        }), 503

    except Exception as e:
        return jsonify({
            "status": "Lỗi",
            "message": f"Thử lại thất bại (Đang đếm lỗi): {str(e)}",
            "breaker_state": circuit.current_state
        }), 500

@app.route('/api/status')
def breaker_status():
    return jsonify({
        "current_state": circuit.current_state,
        "failure_count": circuit.fail_counter,
        "reset_timeout": circuit.reset_timeout
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)