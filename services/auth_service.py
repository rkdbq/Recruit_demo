import base64
import re

# 이메일 형식 검증 함수
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

# 비밀번호 Base64 인코딩 함수
def encode_password(password):
    return base64.b64encode(password.encode('utf-8')).decode('utf-8')