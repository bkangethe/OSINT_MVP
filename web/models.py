from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(255))
    role = db.Column(db.String(20), default="viewer")

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    note = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=db.func.now())
