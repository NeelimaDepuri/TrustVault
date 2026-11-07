from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True)

    email = db.Column(db.String(120), unique=True)

    password = db.Column(db.String(200))

    role = db.Column(db.String(20))


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    filename = db.Column(db.String(200))

    filepath = db.Column(db.String(300))

    owner_id = db.Column(db.Integer)
class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    document_id = db.Column(db.Integer)

    user_email = db.Column(db.String(120))

    access_type = db.Column(db.String(20))

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    action = db.Column(db.String(100))

    user_email = db.Column(db.String(120))

    created_at = db.Column(db.String(100))