from flask_mongoengine import Document
from . import db
from .general import Translation


class Category(Document):
    meta = {"collection": "category"}

    name = db.EmbeddedDocumentListField(Translation)

    @classmethod
    def find_by_id(cls, _id):
        return cls.objects(id=_id).first()

    @classmethod
    def find_all(cls):
        return cls.objects()
