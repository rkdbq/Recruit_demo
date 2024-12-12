from models import db

class AccessToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(1000), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'jti': self.jti,
        }