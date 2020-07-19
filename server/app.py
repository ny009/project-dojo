from flask import Flask
from flask import request, jsonify, render_template
from flask_bcrypt import Bcrypt, check_password_hash
from flask_login import current_user, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

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

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

bcrypt = Bcrypt(app)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route("/api/v1/register", methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')
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
    print(request.form)
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    if role == 'student':
        user = Student.query.filter_by(email=email).first()
    else:
        user = Mentor.query.filter_by(email=email).first()

    if user is not None and check_password_hash(user.password, password):
        return jsonify({'value': "Success"})
    return jsonify({'value': "Fail"})


@app.route("/api/v1/logout")
def logout():
    return jsonify({'value': "Success"})


if __name__ == "__main__":
    app.run(debug=True)
