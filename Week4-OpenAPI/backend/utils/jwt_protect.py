from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request

def protect_blueprint(bp):
    @bp.before_request
    def require_jwt():
        try:
            verify_jwt_in_request()
        except Exception as e:
            return jsonify({'error': 'Unauthorized', 'message': str(e)}), 401
