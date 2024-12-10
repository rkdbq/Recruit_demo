from flask import Flask
from flasgger import Swagger
from models import db
from controllers import register_blueprints

# * 포트 포워딩 정보
#   - 113.198.66.67:10xxx -> 10.0.0.xxx:8080
#   - 113.198.66.67:13xxx -> 10.0.0.xxx:3000
#   - 113.198.66.67:17xxx -> 10.0.0.xxx:443
#   - 113.198.66.67:18xxx -> 10.0.0.xxx:80
#   - 113.198.66.67:19xxx -> 10.0.0.xxx:7777 (ssh)
#   - 위 포트 외는 방화벽으로 차단되어 있습니다.

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)

register_blueprints(app)
swagger = Swagger(app)

def create_tables():
    db.create_all()
    
app.before_request(create_tables)

@app.route("/")
def home():
    return "Server is online"

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=8080
    )