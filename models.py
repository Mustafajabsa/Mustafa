from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String, nullable = False)
    description = db.Column(db.Text, nullable = False)
    technologies = db.Column(db.String(200), nullable = False)
    image_filename = db.Column(db.String(200), nullable = False)
    project_link = db.Column(db.String(200), nullable = False)

    def __repr__(self):
        return f'<project {self.title}>'