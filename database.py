from flask_sqlalchemy import SQLAlchemy
from app import db

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.String(200), nullable=False)
    responses = db.Column(db.PickleType, nullable=False)

def add_content_to_db(prompt, responses):
    content = Content(prompt=prompt, responses=responses)
    db.session.add(content)
    db.session.commit()

def get_content_from_db(prompt):
    content = Content.query.filter_by(prompt=prompt).first()
    if content:
        return content.responses
    return None