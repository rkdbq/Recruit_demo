from models import db

class Company(db.Model):
    """
    회사 정보 모델:
        회사명: String
        대표자명: String (null)
        기업형태: String
        업종: String
        사원수: Integer (null)
        설립일: Date (null)
        홈페이지: String (null)
        기업주소: String (null)
    """
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(50), nullable=False)
    rep_name = db.Column(db.String(50))
    company_type = db.Column(db.String(50), nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    employ_num = db.Column(db.Integer)
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
            'est_date': self.est_date.year if self.est_date else None,  # 연도만 반환
            'homepage': self.homepage,
            'address': self.address,
        }
