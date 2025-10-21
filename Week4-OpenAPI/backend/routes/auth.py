from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == "admin" and password == "123456":
        token = create_access_token(identity=username)
        return jsonify(access_token=token)
    return jsonify({'error': 'Invalid credentials'}), 401
