from . import db
from flask_mongoengine import Document
from datetime import datetime
from .user import User
from .answer import Answer
from .general import Reaction
from .location import City
from .category import Category


class Question(Document):
    meta = {"collection": "questions"}

    created_by = db.ReferenceField(User, required=True)
    title = db.StringField(required=True)
    content = db.StringField()
    approved = db.BooleanField(required=True, default=False)
    creation_date = db.DateTimeField(required=True, default=datetime.utcnow)
    view_count = db.IntField()
    reactions = db.EmbeddedDocumentListField(Reaction)
    images = db.ListField(db.StringField())
    category = db.ReferenceField(Category, required=True, reverse_delete_rule=1)
    location = db.ReferenceField(City, required=True)
    answers = db.ListField(db.ReferenceField(Answer))

    @classmethod
    def find_by_id(cls, _id):
        return cls.objects(id=_id).first()
