from . import db
from flask_mongoengine import Document
from datetime import datetime
from .user import User
from .answer import Answer
from .general import Reaction, Location


class Question(Document):
    meta = {"collection": "questions"}

    created_by = db.ReferenceField(User, required=True)
    title = db.StringField(required=True)
    content = db.StringField()
    approved = db.BooleanField(required=True, default=False)
    creation_date = db.DateTimeField(required=True, default=datetime.utcnow)
    view_count = db.IntField()
    reactions = db.EmbeddedDocumentListField(Reaction)
    images = db.ListField(db.URLField())
    category = db.StringField(required=True)
    location = db.EmbeddedDocumentField(Location, required=True)
    answers = db.ListField(db.ReferenceField(Answer))

    @classmethod
    def find_by_id(cls, _id):
        return cls.objects(id=_id).first()
