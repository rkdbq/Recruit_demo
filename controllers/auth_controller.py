from flask import g, Blueprint, request
from models import db
from models.user_model import User, Log
from models.blacklist_model import AccessToken
from services.jwt_service import jwt_required, decode_jwt_token, generate_jwt_token
from services.auth_service import encode_password, is_valid_email, log_attempt
from views.response import json_response

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def add_user():
    if not request.json or not 'email' in request.json:
        return json_response(code=400, args=request.args.to_dict())

    user = User(
        email=request.json['email'],
        usertype=request.json['usertype'],
        password=request.json['password'],
    )
    
    if not is_valid_email(user.email):
        return json_response(
            code=400, 
            args=request.args.to_dict(), 
            message="Invalid Email Format",
            )
    
    # 중복 회원 검사
    if User.query.filter_by(email=user.email).first():
        return json_response(
            code=409, 
            args=request.args.to_dict(),
            message="Email Already Exists",
            )
    
    # 비밀번호 암호화 (Base64)
    user.password = encode_password(user.password)

    # 사용자 정보 저장
    try:
        db.session.add(user)
        db.session.commit() 

    except Exception as e:
        db.session.rollback()
        return json_response(code=500, args=request.args.to_dict())

    return json_response(
        code=201, 
        args=request.args.to_dict(), 
        data=[user.to_dict()],
        )

@auth_bp.route('/', methods=['DELETE'])
@jwt_required
def delete_user():
    existing_user = g.current_user
    if not existing_user:
        return json_response(code=404, args=request.args.to_dict())
    
    user = User.query.get(existing_user.id)
    if not user:
        return json_response(code=404, args=request.args.to_dict())

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return json_response(code=500, args=request.args.to_dict())

    return json_response(
        code=200, 
        args=request.args.to_dict(), 
        message=f"User with ID {user.id} has been Deleted",
        )

@auth_bp.route('/profile', methods=['GET'])
@jwt_required
def get_user():
    if not request.json:
        return json_response(code=400, args=request.args.to_dict()) 
        
    existing_user = g.current_user
    if not existing_user:
        return json_response(code=404, args=request.args.to_dict())
    
    user = User.query.get(existing_user.id)
    return json_response(
        code=200, 
        args=request.args.to_dict(), 
        data=[user.to_dict()],
        )

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required
def update_user():
    if not request.json:
        return json_response(code=400, args=request.args.to_dict())
        
    existing_user = g.current_user
    if not existing_user:
        return json_response(code=404, args=request.args.to_dict())
    
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
        return json_response(code=500, args=request.args.to_dict())
    
    return json_response(
        code=201, 
        args=request.args.to_dict(), 
        data=[existing_user.to_dict()],
        )

@auth_bp.route('/login', methods=['POST'])
def login():
    log = Log (
        email=request.json.get('email', None),
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
    )
        
    if not request.json or not 'email' in request.json or not 'password' in request.json:
        log_attempt(log, request)
        return json_response(
            code=400, 
            args=request.args.to_dict(), 
            message="Username and password are required",
            )
        
    existing_user = User.query.filter_by(email=request.json['email']).first()
    if not existing_user:
        log_attempt(log, request)
        return json_response(code=404, args=request.args.to_dict())
    
    user = User (
        email=request.json['email'],
        password=request.json['password'],
    )
    
    if existing_user.password == encode_password(user.password):
        log.user_id = existing_user.id
        log.status = "Success"
        log_attempt(log, request)
        return json_response(
            code=200, 
            args=request.args.to_dict(), 
            message="Login Successful",
            data={
                "access_token": generate_jwt_token(existing_user, hours=1),
                "refresh_token": generate_jwt_token(existing_user, days=7),
                },
            )
    else:
        log_attempt(log, request)
        return json_response(
            code=401, 
            args=request.args.to_dict(), 
            message="Invalid username or password",
            )
    
@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    try:
        refresh_token = request.json.get('refresh_token', None)
        old_access_token = request.json.get('old_access_token', None)
        
        if not refresh_token or not old_access_token:
            return json_response(
                code=400, 
                args=request.args.to_dict(), 
                message="Refresh token and Old access token are required",
                )
        
        decoded_rt = decode_jwt_token(refresh_token)
        decoded_old_at = decode_jwt_token(old_access_token)
        
        user = User(
            id=decoded_rt['id'],
            email=decoded_rt['email'],
            usertype=decoded_rt['usertype'],
        )
        
        old_at = AccessToken(
            jti=decoded_old_at['jti'],
        )
        
        try:
            db.session.add(old_at)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return json_response(code=500, args=request.args.to_dict())

        return json_response(
            code=200, 
            args=request.args.to_dict(), 
            message="Access token refreshed",
            data={
                "access_token": generate_jwt_token(user, hours=1),
                },
            )
        
    except Exception as e:
        return json_response(code=500, args=request.args.to_dict())