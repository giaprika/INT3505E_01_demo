from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from models import db, Admin

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/register', methods=['POST'])
def register_admin():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    # Kiểm tra email đã tồn tại chưa
    if Admin.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    # Tạo admin mới
    hashed_pw = generate_password_hash(password)
    admin = Admin(email=email, password_hash=hashed_pw)
    db.session.add(admin)
    db.session.commit()

    return jsonify({
        'message': 'Admin registered successfully',
        'admin_id': admin.id
    }), 201


@admin_bp.route('/login', methods=['POST'])
def login_admin():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    admin = Admin.query.filter_by(email=email).first()
    if not admin or not check_password_hash(admin.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(
        identity=str(admin.id), 
        additional_claims={"email": admin.email}  
    )
    return jsonify({'access_token': access_token})


@admin_bp.route('/me', methods=['GET'])
@jwt_required()
def get_admin_profile():
    current_admin = get_jwt_identity()
    return jsonify({
        'message': 'Authenticated admin',
        'admin': current_admin
    })
