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

@app.route("/")
def home():
    return "There is home"

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/auth/register', methods=['POST'])
def register():
    print(request.json)

    if not request.json or not 'email' in request.json:
        abort(400)

    user = User(
        email=request.json['email'],
        usertype=request.json['usertype'],
        password=request.json['password'],
    )
    
    # 이메일 형식 검증
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_regex, user.email) is None:
        return jsonify({'error': 'Invalid email format'}), 400
    
    # 중복 회원 검사
    if User.query.filter_by(email=user.email).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    # 비밀번호 암호화 (Base64)
    user.password = base64.b64encode(user.password.encode('utf-8')).decode('utf-8')

    # 사용자 정보 저장
    try:
        db.session.add(user)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occured'}), 500

    return jsonify(user.to_dict()), 201

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8080
    )