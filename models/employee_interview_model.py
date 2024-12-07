from models import db

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

class EmployeeInterviewQA(db.Model):
    """
    현직자 인터뷰 QA 모델:
        인터뷰 아이디(FK -> 인터뷰 아이디): Integer
        질문: Text
        응답: Text
    """
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
    """
    현직자 인터뷰 키워드 모델:
        인터뷰 아이디(FK -> 인터뷰 아이디): Integer
        키워드: String
    """
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
