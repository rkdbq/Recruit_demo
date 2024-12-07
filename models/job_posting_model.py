from models import db

class JobPosting(db.Model):
    """
    채용 공고 모델:
        제목: String
        지역: String
        경력: String
        급여: Integer (null)
        기술스택: String (null)
        회사명(FK -> 회사 아이디): Integer
        포지션: String
        조회수: Integer
    """
    id = db.Column(db.Integer, primary_key=True)  # 공고 아이디 (PK)
    title = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=False)  # 지역
    experience = db.Column(db.String(50), nullable=False)  # 경력
    salary = db.Column(db.Integer)  # 급여
    tech_stack = db.Column(db.String(200))  # 기술 스택
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)  # 회사명 (FK -> 회사 아이디)
    position = db.Column(db.String(50), nullable=False)  # 포지션
    views = db.Column(db.Integer, default=0)  # 조회수
    
    # 회사와의 관계 설정
    company = db.relationship('Company', backref=db.backref('job_postings', lazy=True))
    
    keywords = db.relationship('JobPostingKeyword', backref='job_posting', cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='job_posting', cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='job_posting', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'location': self.location,
            'experience': self.experience,
            'salary': self.salary,
            'tech_stack': self.tech_stack,
            'company_id': self.company_id,
            'position': self.position,
            'views': self.views,
        }
        
    def to_summerized_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company_id': self.company_id,
        }

class JobPostingKeyword(db.Model):
    """
    채용 공고 키워드 모델:
        공고 아이디(FK -> 공고 아이디): Integer
        키워드: String
    """
    id = db.Column(db.Integer, primary_key=True)  # 공고 키워드 아이디 (PK)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'), nullable=False)  # 공고 아이디 (FK -> 공고 아이디)
    keyword = db.Column(db.String(50), nullable=False)  # 키워드
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_posting_id': self.job_posting_id,
            'keyword': self.keyword,
        }
