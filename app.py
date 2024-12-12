from waitress import serve
from flask import Flask
from flasgger import Swagger
from models import db
from controllers import register_blueprints

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
    serve(
        app=app,
        host="0.0.0.0",
        port=8080,
    )
