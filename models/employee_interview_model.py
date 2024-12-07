from models import db

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
