from flask import abort, g, jsonify, Blueprint, request
from models import db
from models.user_model import User
from services.jwt_service import jwt_required, generate_jwt_token
from services.auth_service import encode_password, is_valid_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def add_user():
    if not request.json or not 'email' in request.json:
        abort(400)

    user = User(
        email=request.json['email'],
        usertype=request.json['usertype'],
        password=request.json['password'],
    )
    
    if not is_valid_email(user.email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # 중복 회원 검사
    if User.query.filter_by(email=user.email).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    # 비밀번호 암호화 (Base64)
    user.password = encode_password(user.password)

    # 사용자 정보 저장
    try:
        db.session.add(user)
        db.session.commit() 

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occured'}), 500

    return jsonify(user.to_dict()), 201

@auth_bp.route('/', methods=['DELETE'])
@jwt_required
def delete_user():
    existing_user = g.current_user
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
    
    user = User.query.get(existing_user.id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

    return jsonify({'message': f'User with ID {user.id} has been deleted'}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required
def get_user():
    if not request.json:
            abort(400)
        
    existing_user = g.current_user
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
    
    user = User.query.get(existing_user.id)
    return jsonify(user.to_dict())

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required
def update_user():
    if not request.json:
        abort(400)
        
    existing_user = g.current_user
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
    
    new_user = User(
        usertype=request.json.get('usertype', None),
        password=request.json.get('password', None),
    )
    
    try:
        if new_user.usertype:
            existing_user.usertype = new_user.usertype
        if new_user.password:
            existing_user.password = encode_password(new_user.password)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    
    return jsonify(existing_user.to_dict()), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    if not request.json or not 'email' in request.json:
        abort(400)
        
    if not 'password' in request.json:
        return jsonify({"error": "Username and password are required"}), 400
        
    existing_user = User.query.filter_by(email=request.json['email']).first()
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
    
    user = User (
        email=request.json['email'],
        password=request.json['password'],
    )
    
    if existing_user.password == encode_password(user.password):
        access_token = generate_jwt_token(existing_user, hours=1)
        refresh_token = generate_jwt_token(existing_user, days=7)
        return jsonify({
            "message": "Login successful", 
            "access_token": access_token,
            "refresh_token": refresh_token,
            }), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401
    
# @auth_bp.route('/auth/refresh', methods=['POST'])
# def refresh():
#     try:
#         refresh_token = request.json.get('refresh_token', None)
        
#         if not refresh_token:
#             return jsonify({"error": "Refresh token is required"}), 400
        
#         try:
#             decoded_token = jwt.decode(refresh_token, app.config['SECRET_KEY'], algorithms=["HS256"])
#         except jwt.ExpiredSignatureError:
#             return jsonify({"error": "Refresh token has expired"}), 401
#         except jwt.InvalidTokenError:
#             return jsonify({"error": "Invalid refresh token"}), 401
        
#         user = User(
#             id=decoded_token['id'],
#             email=decoded_token['email'],
#             usertype=decoded_token['usertype'],
#         )
#         new_access_token = generate_jwt_token(user, hours=1)
        
#         return jsonify({
#             "message": "Access token refreshed",
#             "access_token": new_access_token
#         }), 200
        
#     except Exception as e:
#         return jsonify({"error": "An error occurred", "details": str(e)}), 500