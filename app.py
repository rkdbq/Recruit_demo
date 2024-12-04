from flask import Flask, request, jsonify, abort, render_template
from models.user import db, User

import os, re, base64

# * 포트 포워딩 정보
#   - 113.198.66.67:10xxx -> 10.0.0.xxx:8080
#   - 113.198.66.67:13xxx -> 10.0.0.xxx:3000
#   - 113.198.66.67:17xxx -> 10.0.0.xxx:443
#   - 113.198.66.67:18xxx -> 10.0.0.xxx:80
#   - 113.198.66.67:19xxx -> 10.0.0.xxx:7777 (ssh)
#   - 위 포트 외는 방화벽으로 차단되어 있습니다.

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@localhost:3000/wsd3_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def create_tables():
    db.create_all()
    
app.before_request(create_tables)

# 이메일 형식 검증 함수
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# 비밀번호 Base64 인코딩 함수
def encode_password(password):
    return base64.b64encode(password.encode('utf-8')).decode('utf-8')

@app.route("/")
def home():
    return "There is home"

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/auth/register', methods=['POST'])
def register():
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

@app.route('/auth/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

    return jsonify({'message': f'User with ID {user_id} has been deleted'}), 200

@app.route('/auth/profile', methods=['PUT'])
def update_profile():
    if not request.json or not 'email' in request.json:
        abort(400)
        
    user = User(
        email=request.json['email'],
        usertype=request.json.get('usertype', ""),
        password=request.json.get('password', ""),
    )
        
    existing_user = User.query.filter_by(email=user.email).first()
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        if user.usertype != "":
            existing_user.usertype = user.usertype
        if user.password != "":
            existing_user.password = encode_password(user.password)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    
    return jsonify(existing_user.to_dict()), 201


if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8080
    )