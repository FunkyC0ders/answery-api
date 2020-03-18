from . import db
from flask_mongoengine import Document
from datetime import datetime
from .user import User
from .general import Reaction


class Replies(Document):
    meta = {"collection": "answers", "allow_inheritance": True}
    created_by = db.ReferenceField(User, required=True)
    content = db.StringField()
    creation_date = db.DateTimeField(required=True, default=datetime.utcnow)
    reactions = db.EmbeddedDocumentListField(Reaction)


class Answer(Replies):
    replies = db.ListField(db.ReferenceField(Replies))
