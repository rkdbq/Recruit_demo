import base64
import datetime, os, jwt
from functools import wraps
from flask import g, request
from models.user_model import User
from models.blacklist_model import AccessToken
from views.response import json_response

SECRET_KEY = os.environ['SECRET_KEY']

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        # 헤더에서 JWT 토큰 추출
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # "Bearer <token>"
        
        if not token:
            return json_response(
                code=401, 
                args=request.args.to_dict(), 
                message="Token is missing",
                )

        try:
            # 토큰 디코딩
            decoded_at = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            blocked_at = AccessToken.query.filter_by(jti=decoded_at['jti']).first()
            if blocked_at:
                return json_response(
                    code=401, 
                    args=request.args.to_dict(), 
                    message="Token is blacklisted",
                    )
            # 인증된 사용자 정보 조회
            user = User.query.filter_by(email=decoded_at['email']).first()
            if not user:
                return json_response(
                    code=401, 
                    args=request.args.to_dict(), 
                    message="Invalid token",
                    )
            # g 객체에 사용자 정보 저장
            g.current_user = user
        except jwt.ExpiredSignatureError:
            return json_response(
                code=401, 
                args=request.args.to_dict(), 
                message="Token has expired",
                )
            
        except jwt.InvalidTokenError:
            return json_response(
                code=401, 
                args=request.args.to_dict(), 
                message="Invalid token",
                )

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
                "exp": exp,
                "jti": generate_jti()
            },
            SECRET_KEY,
            algorithm="HS256",
        )
    
def decode_jwt_token(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            
    except jwt.ExpiredSignatureError:
        return json_response(
            code=401, 
            args=request.args.to_dict(), 
            message="Token has expired",
            )
    except jwt.InvalidTokenError:
        return json_response(
            code=401, 
            args=request.args.to_dict(), 
            message="Invalid token",
            )
    
    return decoded_token

def generate_jti():
    return base64.b64encode(os.urandom(16)).decode('utf-8')
