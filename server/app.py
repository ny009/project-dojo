from flask import Flask
from flask import request, jsonify, render_template
from flask_bcrypt import Bcrypt, check_password_hash
from flask_login import current_user, logout_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

db = SQLAlchemy()


class Mentor(db.Model, UserMixin):
    mentor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    projects = db.relationship("Project")


class Student(db.Model, UserMixin):
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


class Project(db.Model):
    project_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    outline = db.Column(db.String, nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.mentor_id'))

class Groups(db.Model):
    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.mentor_id'))


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
    req = request.get_json(force=True)
    name = req['name']
    email = req['email']
    password = req['password']
    role = req['role']
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
    req = request.get_json(force=True)
    email = req['email']
    password = req['password']
    role = req['role']

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


@app.route("/api/v1/project", methods=['POST'])
def create_project():
    req = request.get_json(force=True)
    title = req['title']
    outline = req['outline']
    mentor = req['mentor']

    project = Project(title=title, outline=outline, mentor_id=mentor)
    db.session.add(project)
    db.session.commit()

    return jsonify({'value': "Success"})


@app.route("/api/v1/project", methods=['GET'])
def get_project_by_mentor():
    mentor_id = request.args.get('mentor', type=int)

    projects = Project.query.filter_by(mentor_id=mentor_id).all()

    return jsonify(projects)


@app.route("/api/v1/group", methods=['POST'])
def make_group():
    req = request.get_json(force=True)
    name = req['name']
    expiry_date = req['expiry_date']
    mentor = req['mentor']

    project = Groups(name=name, expiry_date=expiry_date, mentor_id=mentor)
    db.session.add(project)
    db.session.commit()

    return jsonify({'value': "Success"})


if __name__ == "__main__":
    app.run(debug=True)
