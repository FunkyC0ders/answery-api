from . import db
from flask_mongoengine import Document
from datetime import datetime
from .user import User
from .general import Reaction


class Reply(Document):
    meta = {"collection": "answers", "allow_inheritance": True}

    created_by = db.ReferenceField(User, required=True)
    content = db.StringField(required=True)
    creation_date = db.DateTimeField(required=True, default=datetime.utcnow)
    reactions = db.EmbeddedDocumentListField(Reaction)

    @classmethod
    def find_by_id(cls, _id):
        return cls.objects(id=_id).first()


class Answer(Reply):
    replies = db.ListField(db.ReferenceField(Reply))
