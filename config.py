import os

class Config:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@localhost:3000/wsd3_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False