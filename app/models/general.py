from . import db
from .user import User


class Location(db.EmbeddedDocument):
    country = db.StringField(required=True)
    city = db.StringField(required=True)


class Reaction(db.EmbeddedDocument):
    user = db.LazyReferenceField(User, required=True)
    reaction = db.StringField(required=True, choices=["like", "dislike"])
