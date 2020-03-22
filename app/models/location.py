from flask_mongoengine import Document
from . import db
from .general import Translation


class Location(Document):
    country = db.EmbeddedDocumentListField(Translation, required=True)
    city = db.EmbeddedDocumentListField(Translation, required=True)

    @classmethod
    def find_by_id(cls, _id):
        return cls.objects(id=_id).first()

    @classmethod
    def find_all(cls):
        return cls.objects()
