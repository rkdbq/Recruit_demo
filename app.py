from flask import Flask, request, jsonify, abort
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://rkdbq_local:Kang1293!!@localhost/wsd3_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def create_tables():
    db.create_all()
    
app.before_request(create_tables)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/users', methods=['POST'])
def create_student():
    print(request.json)

    if not request.json or not 'username' in request.json:
        abort(400)

    user = User(
        username=request.json['username'],
        usertype=request.json.get('usertype', 0),
        password=request.json.get('password', "")
    )

    try:
        db.session.add(user)
        db.session.commit()

    except Exception as e:
        print(e)
        return jsonify({'error': 'User already exists'}), 409

    return jsonify(user.to_dict()), 201

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=3000
    )