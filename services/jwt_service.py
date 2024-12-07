import datetime, os, jwt
from functools import wraps
from flask import g, jsonify, request
from models.user_model import User

SECRET_KEY = os.environ['SECRET_KEY']

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        # 헤더에서 JWT 토큰 추출
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # "Bearer <token>"
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            # 토큰 디코딩
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            # 인증된 사용자 정보 조회
            user = User.query.filter_by(email=data['email']).first()
            if not user:
                return jsonify({'error': 'Invalid token'}), 401
            # g 객체에 사용자 정보 저장
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated_function

def generate_jwt_token(user, hours=None, days=None):
    exp = datetime.datetime.utcnow()
    if hours:
        exp += datetime.timedelta(hours=1)
    elif days:
        exp += datetime.timedelta(days=1)
        
    return jwt.encode(
            {
                "id": user.id,
                "email": user.email,
                "usertype": user.usertype,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            },
            SECRET_KEY,
            algorithm="HS256",
        )
    
def decode_jwt_token(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    
    return decoded_token