from flask import Flask
from flask import request, jsonify, render_template
from flask_bcrypt import Bcrypt, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from sqlalchemy import text

db = SQLAlchemy()


class Mentor(db.Model):
    mentor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    projects = db.relationship("Project")


class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)


class Project(db.Model):
    project_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    outline = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.mentor_id'))


class Team(db.Model):
    team_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('POSTGRES_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

bcrypt = Bcrypt(app)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

version = "v2"


@app.route('/')
def list_api():
    return render_template('index.html')


@app.route(f"/api/{version}/register", methods=['POST'])
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


@app.route(f"/api/{version}/login", methods=['POST'])
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
        if role == 'student':
            return jsonify({"id": user.student_id, "name": user.name})
        else:
            return jsonify({"id": user.mentor_id, "name": user.name})

    return jsonify({'value': "Fail"})


@app.route(f"/api/{version}/logout")
def logout():
    return jsonify({'value': "Success"})


@app.route(f"/api/{version}/project", methods=['POST'])
def create_project():
    req = request.get_json(force=True)
    title = req['title']
    outline = req['outline']
    start_date = req['start_date']
    end_date = req['end_date']
    mentor = req['mentor']

    project = Project(title=title, outline=outline,
                      start_date=start_date, end_date=end_date, mentor_id=mentor)
    db.session.add(project)
    db.session.commit()

    return jsonify({'value': "Success"})


@app.route(f"/api/{version}/project", methods=['GET'])
def get_project_by_mentor():
    mentor_id = request.args.get('mentor', type=int)
    if mentor_id is not None:
        projects = Project.query.filter_by(mentor_id=mentor_id).all()
    else:
        projects = Project.query.all()

    return jsonify(projects)


@app.route(f"/api/{version}/project/enroll", methods=['POST'])
def enroll_project():
    req = request.get_json(force=True)
    project_id = req['project_id']
    student_id = req['student_id']

    sql = f"INSERT INTO student_project(project_id, student_id) VALUES({project_id}, {student_id});"
    db.session.execute(text(sql))
    db.session.commit()

    return jsonify({'value': "Success"})


@app.route(f"/api/{version}/team", methods=['POST'])
def create_team():
    req = request.get_json(force=True)
    student_id = req['student_id']
    project_id = req['project_id']
    name = req['name']

    team = Team(name=name)
    db.session.add(team)
    db.session.flush()

    team_id = team.team_id

    sql = f"INSERT INTO student_team(team_id, student_id) VALUES({team_id}, {student_id});"
    db.session.execute(text(sql))
    db.session.commit()

    sql = f"INSERT INTO project_team(team_id, project_id) VALUES({team_id}, {project_id});"
    db.session.execute(text(sql))
    db.session.commit()

    return jsonify({'value': "Success"})


if __name__ == "__main__":
    app.run(debug3=True)
