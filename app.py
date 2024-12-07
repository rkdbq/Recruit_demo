from flask import Flask, request, jsonify, abort, render_template, g
from models.user import Bookmark, Company, db, User, JobPosting, Application, JobPostingKeyword

import os, re, base64, jwt, datetime
from functools import wraps

# * 포트 포워딩 정보
#   - 113.198.66.67:10xxx -> 10.0.0.xxx:8080
#   - 113.198.66.67:13xxx -> 10.0.0.xxx:3000
#   - 113.198.66.67:17xxx -> 10.0.0.xxx:443
#   - 113.198.66.67:18xxx -> 10.0.0.xxx:80
#   - 113.198.66.67:19xxx -> 10.0.0.xxx:7777 (ssh)
#   - 위 포트 외는 방화벽으로 차단되어 있습니다.

SECRET_KEY = os.environ['SECRET_KEY']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@localhost:3000/wsd3_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def create_tables():
    db.create_all()
    
app.before_request(create_tables)

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

# 이메일 형식 검증 함수
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# 비밀번호 Base64 인코딩 함수
def encode_password(password):
    return base64.b64encode(password.encode('utf-8')).decode('utf-8')

# @app.route("/")
# def home():
#     return "Server is online"

# @app.route('/auth', methods=['GET'])
# def get_users():
#     users = User.query.all()
#     return jsonify([user.to_dict() for user in users])

@app.route('/auth/register', methods=['POST'])
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

@app.route('/auth/profile', methods=['GET'])
@jwt_required
def get_user():
    if not request.json:
            abort(400)
        
    existing_user = g.current_user
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
    
    user = User.query.get(existing_user.id)
    return jsonify(user.to_dict())

@app.route('/auth/profile', methods=['PUT'])
@jwt_required
def update_user():
    if not request.json:
        abort(400)
        
    existing_user = g.current_user
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
    
    user = User(
        usertype=request.json.get('usertype', None),
        password=request.json.get('password', None),
    )
    
    try:
        if user.usertype:
            existing_user.usertype = user.usertype
        if user.password:
            existing_user.password = encode_password(user.password)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    
    return jsonify(existing_user.to_dict()), 201

@app.route('/auth/login', methods=['POST'])
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
        access_token = jwt.encode(
            {
                "id": existing_user.id,
                "email": existing_user.email,
                "usertype": existing_user.usertype,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            },
            SECRET_KEY,
            algorithm="HS256",
        )
        refresh_token = jwt.encode(
            {
                "id": existing_user.id,
                "email": existing_user.email,
                "usertype": existing_user.usertype,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
            },
            SECRET_KEY,
            algorithm="HS256",
        )
        return jsonify({
            "message": "Login successful", 
            "access_token": access_token,
            "refresh_token": refresh_token,
            }), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401
    
@app.route('/auth/refresh', methods=['POST'])
def refresh():
    try:
        refresh_token = request.json.get('refresh_token', None)
        
        if not refresh_token:
            return jsonify({"error": "Refresh token is required"}), 400
        
        try:
            decoded_token = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Refresh token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid refresh token"}), 401
        
        new_access_token = jwt.encode(
            {
                "id": decoded_token['id'],
                "email": decoded_token['email'],
                "usertype": decoded_token['usertype'],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            },
            SECRET_KEY,
            algorithm="HS256",
        )
        
        return jsonify({
            "message": "Access token refreshed",
            "access_token": new_access_token
        }), 200
        
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500
        
@app.route('/companies', methods=['GET'])
def get_companies():
    companies = Company.query.all()
    return jsonify([company.to_dict() for company in companies])

@app.route('/companies', methods=['POST'])
def add_company():
    if not request.json:
        abort(400)

    company = Company(
        company_name=request.json['company_name'],
        rep_name=request.json.get('rep_name', None),
        company_type=request.json['company_type'],
        industry=request.json['industry'],
        employ_num=request.json.get('employ_num', None),
        est_date=request.json.get('est_date', None),
        homepage=request.json.get('homepage', None),
        address=request.json.get('address', None),
    )
    
    # 채용 공고 저장
    try:
        db.session.add(company)
        db.session.commit() 

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occured'}), 500

    return jsonify(company.to_dict()), 201

@app.route('/jobs', methods=['GET'])
def get_jobs():
    page = request.args.get('page', 1, type=int)
    location = request.args.get('location', type=str)
    experience = request.args.get('experience', type=str)
    salary_min = request.args.get('salary_min', type=int)
    salary_max = request.args.get('salary_max', type=int)
    tech_stack = request.args.get('tech_stack', type=str)
    company_id = request.args.get('company_id', type=int)
    position = request.args.get('position', type=str)
    keyword = request.args.get('keyword', type=str)  # 추가된 키워드 필터
    sort_by = request.args.get('sort_by', 'id', type=str)  # 기본 정렬: id
    sort_order = request.args.get('sort_order', 'asc', type=str)  # asc or desc
    
    query = JobPosting.query
    
    # 필터링
    if location:
        query = query.filter(JobPosting.location.ilike(f"%{location}%"))
    if experience:
        query = query.filter(JobPosting.experience.ilike(f"%{experience}%"))
    if salary_min is not None:
        query = query.filter(JobPosting.salary >= salary_min)
    if salary_max is not None:
        query = query.filter(JobPosting.salary <= salary_max)
    if tech_stack:
        query = query.filter(JobPosting.tech_stack.ilike(f"%{tech_stack}%"))
    if company_id is not None:
        query = query.filter(JobPosting.company_id == company_id)
    if position:
        query = query.filter(JobPosting.position.ilike(f"%{position}%"))
    if keyword:
        query = query.join(JobPostingKeyword).filter(JobPostingKeyword.keyword.ilike(f"%{keyword}%"))
        
    # 정렬
    if sort_order.lower() == 'desc':
        query = query.order_by(getattr(JobPosting, sort_by).desc())
    else:
        query = query.order_by(getattr(JobPosting, sort_by).asc())
    
    jobs = query.paginate(page=page, per_page=20, error_out=False)
    return jsonify([job.to_summerized_dict() for job in jobs])

@app.route('/jobs/<int:job_id>', methods=['GET'])
def get_job_detail(job_id):
    job = JobPosting.query.get(job_id)
    try:
        job.views += 1
        db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occured'}), 500
    
    return jsonify(job.to_dict())

@app.route('/jobs', methods=['POST'])
def add_job():
    if not request.json or not 'company_id' in request.json:
        abort(400)

    job_posting = JobPosting(
        title=request.json['title'],
        location=request.json['location'],
        experience=request.json['experience'],
        salary=request.json.get('salary', None),
        tech_stack=request.json.get('tech_stack', None),
        company_id=request.json['company_id'],
        position=request.json['position'],
        views=request.json.get('views', None),
    )
    
    # 채용 공고 저장
    try:
        db.session.add(job_posting)
        db.session.commit() 

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occured'}), 500

    for keyword in request.json['keywords']:
        job_posing_keyword = JobPostingKeyword(
            job_posting_id=job_posting.id,
            keyword=keyword,
        )
        try:
            db.session.add(job_posing_keyword)
            db.session.commit()
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Database error occured'}), 500
        
    return jsonify(job_posting.to_dict()), 201

@app.route('/applications', methods=['POST'])
@jwt_required
def apply():
    existing_user = g.current_user
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
    
    if not request.json or not 'job_posting_id' in request.json:
        abort(400)
            
    new_application = Application(
        job_posting_id=request.json['job_posting_id'],
        user_id=existing_user.id,
        status="지원 완료",
        applied_date=datetime.datetime.now(),
        resume=request.json.get('resume', None)
    )
    
    existing_application = Application.query.filter_by(job_posting_id=new_application.job_posting_id,
                                                       user_id=new_application.user_id).first()
    
    application = existing_application
    if not existing_application:
        application = new_application
        try:
            db.session.add(new_application)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Database error occurred'}), 500
    elif existing_application.status == "지원 취소":
        try:
            existing_application.status = "지원 완료"
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Database error occurred'}), 500
        
    return jsonify(application.to_dict()), 201

@app.route('/applications', methods=['GET'])
@jwt_required
def get_applications():
    existing_user = g.current_user
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
    
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', type=str)
    sort_by = request.args.get('sort_by', 'id', type=str)  # 기본 정렬: id
    sort_order = request.args.get('sort_order', 'asc', type=str)  # asc or desc
    
    query = Application.query.filter_by(user_id=existing_user.id)

    # 필터링
    if status:
        query = query.filter(Application.status.ilike(f"%{status}%"))
        
    # 정렬
    if sort_order.lower() == 'desc':
        query = query.order_by(getattr(Application, sort_by).desc())
    else:
        query = query.order_by(getattr(Application, sort_by).asc())
        
    applications = query.paginate(page=page, per_page=20, error_out=False)
    return jsonify([app.to_dict() for app in applications])

@app.route('/applications/<int:id>', methods=['DELETE'])
@jwt_required
def delete_application(id):
    existing_user = g.current_user
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
    
    application = Application.query.filter_by(id=id,
                                              user_id=existing_user.id).first()
    if not application:
        return jsonify({'error': 'Application not found'}), 404

    try:
        if application.status == "지원 취소":
            return jsonify({'error': f'Application with Id {application.id} is already canceled'}), 409
        application.status = "지원 취소"
        db.session.commit()
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

    return jsonify({'message': f'Application with ID {application.id} has been deleted'}), 200

@app.route('/bookmarks', methods=['POST'])
@jwt_required
def toggle_bookmark():
    existing_user = g.current_user
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
    
    if not request.json or not 'job_posting_id' in request.json:
        abort(400)
            
    new_bookmark = Bookmark(
        user_id=existing_user.id,
        job_posting_id=request.json['job_posting_id'],
        bookmarked_date=datetime.datetime.now(),
    )
    
    existing_bookmark = Bookmark.query.filter_by(job_posting_id=new_bookmark.job_posting_id,
                                                       user_id=new_bookmark.user_id).first()
    
    bookmark = existing_bookmark
    if not existing_bookmark:
        bookmark = new_bookmark
        try:
            db.session.add(bookmark)
            db.session.commit()
            return jsonify(bookmark.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Database error occurred'}), 500
    else:
        try:
            db.session.delete(bookmark)
            db.session.commit()
            return jsonify({'message': f'Bookmark with ID {bookmark.id} has been deleted'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Database error occurred'}), 500
        
@app.route('/bookmarks', methods=['GET'])
@jwt_required
def get_bookmark():
    existing_user = g.current_user
    if not existing_user:
        return jsonify({'error': 'User not found'}), 404
            
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'bookmarked_date', type=str)  # 기본 정렬: id
    sort_order = request.args.get('sort_order', 'asc', type=str)  # asc or desc
    
    query = Bookmark.query.filter_by(user_id=existing_user.id)
        
    # 정렬
    if sort_order.lower() == 'desc':
        query = query.order_by(getattr(Bookmark, sort_by).desc())
    else:
        query = query.order_by(getattr(Bookmark, sort_by).asc())
        
    bookmarks = query.paginate(page=page, per_page=20, error_out=False)
    return jsonify([bookmark.to_dict() for bookmark in bookmarks])

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8080
    )