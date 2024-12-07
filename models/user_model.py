from models import db
        
class User(db.Model):
    """
    사용자 정보 모델:
        이메일: String
        가입 유형: String
        해싱된 비밀번호: String
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    usertype = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'usertype': self.usertype,
            'password': self.password,
        }
        
class Application(db.Model):
    """
    지원 내역 모델:
        지원자(FK -> 사용자 아이디): Int
        지원 공고(FK -> 채용 공고 아이디): Int
        지원 상태: String
        지원 날짜: DateTime
        첨부 이력서: String (null)
    """
    id = db.Column(db.Integer, primary_key=True)  # 지원 내역 아이디 (PK)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 지원자 (FK -> 사용자 아이디)
    status = db.Column(db.String(50), nullable=False)  # 지원 상태
    applied_date = db.Column(db.DateTime, nullable=False)  # 지원 날짜
    resume = db.Column(db.String(200))  # 첨부 이력서 (파일 경로 저장)

    # 사용자와의 관계 설정
    user = db.relationship('User', backref=db.backref('applications', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_posting_id': self.job_posting_id,
            'user_id': self.user_id,
            'status': self.status,
            'applied_date': self.applied_date,
            'resume': self.resume,
        }

class Bookmark(db.Model):
    """
    북마크/관심공고 모델:
        사용자 아이디(FK -> 사용자 아이디): Integer
        공고 아이디(FK -> 공고 아이디): Integer
        북마크 날짜: DateTime
    """
    id = db.Column(db.Integer, primary_key=True)  # 북마크 아이디 (PK)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 사용자 아이디 (FK -> 사용자 아이디)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'), nullable=False)  # 공고 아이디 (FK -> 공고 아이디)
    bookmarked_date = db.Column(db.DateTime, nullable=False)  # 북마크 날짜

    # 사용자 및 공고와의 관계 설정
    user = db.relationship('User', backref=db.backref('bookmarks', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_posting_id': self.job_posting_id,
            'bookmarked_date': self.bookmarked_date,
        }
           
class EmployeeInterview(db.Model):
    """
    현직자 인터뷰 모델:
        작성자(FK -> 사용자 아이디): Integer
        기업(FK -> 기업 아이디): Interger
        제목: String
        인터뷰이: String
        날짜: DateTime
        조회수: Interger
    """
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
