from flask import Flask
from flask import redirect, request, jsonify
from flask_bcrypt import Bcrypt, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from datetime import datetime

db = None

class Mentor(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Student(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


app = Flask(__name__)

bcrypt = Bcrypt(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route("/api/v1/register", methods=['POST'])
def register():
    name = request.args.get('name')
    email = request.args.get('email')
    password = request.args.get('password')
    role = request.args.get('role')
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
    user = ''
    if user is not None and check_password_hash(password, password):
        return jsonify({'signed_in': True})
    return jsonify({'signed_in': False})


@app.route("/api/v1/logout")
def logout():
    logout_user()
    return jsonify({'logged_out': True})


if __name__ == "__main__":
    app.run(debug=True)