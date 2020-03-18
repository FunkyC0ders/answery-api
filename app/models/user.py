from . import db
from flask_mongoengine import Document
from datetime import datetime


class User(Document):
    meta = {"collection": "users", "allow_inheritance": True}

    name = db.StringField(required=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    avatar = db.URLField()
    creation_date = db.DateTimeField(required=True, default=datetime.utcnow)
    verified = db.BooleanField(required=True, default=False)

    @classmethod
    def find_by_id(cls, _id):
        return cls.objects(id=_id).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.objects(email=email).first()
