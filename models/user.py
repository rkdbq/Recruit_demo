from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy 인스턴스 생성
db = SQLAlchemy()
        
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    usertype = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'usertype': self.usertype,
            'password': self.password,
        }
        
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 지원 내역 아이디 (PK)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 지원자 (FK -> 사용자 아이디)
    status = db.Column(db.String(50), nullable=False)  # 지원 상태
    applied_date = db.Column(db.DateTime, nullable=False)  # 지원 날짜
    resume = db.Column(db.String(200), nullable=True)  # 첨부 이력서 (파일 경로 저장)

    # 사용자와의 관계 설정
    user = db.relationship('User', backref=db.backref('applications', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'applied_date': self.applied_date,
            'resume': self.resume,
        }

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 북마크 아이디 (PK)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 사용자 아이디 (FK -> 사용자 아이디)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'), nullable=False)  # 공고 아이디 (FK -> 공고 아이디)
    bookmarked_date = db.Column(db.DateTime, nullable=False)  # 북마크 날짜

    # 사용자 및 공고와의 관계 설정
    user = db.relationship('User', backref=db.backref('bookmarks', lazy=True))
    job_posting = db.relationship('JobPosting', backref=db.backref('bookmarks', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_posting_id': self.job_posting_id,
            'bookmarked_date': self.bookmarked_date,
        }
        
        
class EmployeeInterview(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 인터뷰 아이디 (PK)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 작성자 (FK -> 사용자 아이디)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)  # 기업 (FK -> 기업 아이디)
    title = db.Column(db.String(100), nullable=False)  # 제목
    interviewee = db.Column(db.String(50), nullable=False)  # 인터뷰이
    date = db.Column(db.DateTime, nullable=False)  # 날짜
    views = db.Column(db.Integer, default=0)  # 조회수

    # 작성자 및 기업과의 관계 설정
    author = db.relationship('User', backref=db.backref('interviews', lazy=True))
    company = db.relationship('Company', backref=db.backref('interviews', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'author_id': self.author_id,
            'company_id': self.company_id,
            'title': self.title,
            'interviewee': self.interviewee,
            'date': self.date,
            'views': self.views,
        }

class EmployeeInterviewQA(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 질문-답변 아이디 (PK)
    interview_id = db.Column(db.Integer, db.ForeignKey('employee_interview.id'), nullable=False)  # 인터뷰 아이디 (FK -> 인터뷰 아이디)
    question = db.Column(db.Text, nullable=False)  # 질문
    answer = db.Column(db.Text, nullable=False)  # 답변

    # 인터뷰와의 관계 설정
    interview = db.relationship('EmployeeInterview', backref=db.backref('qa_pairs', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'interview_id': self.interview_id,
            'question': self.question,
            'answer': self.answer,
        }

class EmployeeInterviewKeyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 인터뷰 키워드 아이디 (PK)
    interview_id = db.Column(db.Integer, db.ForeignKey('employee_interview.id'), nullable=False)  # 인터뷰 아이디 (FK -> 인터뷰 아이디)
    keyword = db.Column(db.String(50), nullable=False)  # 키워드

    # 인터뷰와의 관계 설정
    interview = db.relationship('EmployeeInterview', backref=db.backref('keywords', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'interview_id': self.interview_id,
            'keyword': self.keyword,
        }
        
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(50), nullable=False)
    rep_name = db.Column(db.String(50))
    company_type = db.Column(db.String(50), nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    employ_num = db.Column(db.String(50))
    est_date = db.Column(db.Date)
    homepage = db.Column(db.String(50))
    address = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'rep_name': self.rep_name,
            'company_type': self.company_type,
            'industry': self.industry,
            'employ_num': self.employ_num,
            'est_date': self.est_date,
            'homepage': self.homepage,
            'address': self.address,
        }
        
class JobPosting(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 공고 아이디 (PK)
    location = db.Column(db.String(50), nullable=False)  # 지역
    experience = db.Column(db.String(50), nullable=False)  # 경력
    salary = db.Column(db.String(50))  # 급여
    tech_stack = db.Column(db.String(200))  # 기술 스택
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)  # 회사명 (FK -> 회사 아이디)
    position = db.Column(db.String(50), nullable=False)  # 포지션
    views = db.Column(db.Integer, default=0)  # 조회수
    details = db.Column(db.Text)  # 상세정보
    
    # 회사와의 관계 설정
    company = db.relationship('Company', backref=db.backref('job_postings', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'location': self.location,
            'experience': self.experience,
            'salary': self.salary,
            'tech_stack': self.tech_stack,
            'company_id': self.company_id,
            'position': self.position,
            'views': self.views,
            'details': self.details,
        }

class JobPostingKeyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 공고 키워드 아이디 (PK)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'), nullable=False)  # 공고 아이디 (FK -> 공고 아이디)
    keyword = db.Column(db.String(50), nullable=False)  # 키워드

    # 채용 공고와의 관계 설정
    job_posting = db.relationship('JobPosting', backref=db.backref('keywords', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_posting_id': self.job_posting_id,
            'keyword': self.keyword,
        }