from flask import Flask
from flask import request, jsonify
from flask_bcrypt import Bcrypt, check_password_hash
from flask_login import current_user, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Mentor(db.Model, UserMixin):
    mentor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


class Student(db.Model, UserMixin):
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://rrelepnixlppyi:80ab34ef14e38574ff6bcfc2d4e55d6a2f06c72933ffd95e9509dec552d698da@ec2-3-216-129-140.compute-1.amazonaws.com:5432/d75dva3dnbli8b'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

bcrypt = Bcrypt(app)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route("/api/v1/register", methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.args.get('role')
    print(role)
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    if role == 'student':
        user = Student(name=name, email=email, password=hashed_password)
    else:
        user = Mentor(name=name, email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'value': "Success"})


@app.route("/api/v1/login", methods=['POST'])
def login():
    if current_user.is_authenticated:
        return ""
    email = request.args.get('email')
    password = request.args.get('password')
    role = request.args.get('role')
    if role == 'student':
        sql = f"SELECT password FROM student WHERE email = {email}"
    else:
        sql = f"SELECT password FROM mentor WHERE email = {email}"

    user = db.session.query(sql)
    if user is not None and check_password_hash(user.password, password):
        return jsonify({'signed_in': True})
    return jsonify({'signed_in': False})


@app.route("/api/v1/logout")
def logout():
    logout_user()
    return jsonify({'logged_out': True})


if __name__ == "__main__":
    app.run(debug=True)
