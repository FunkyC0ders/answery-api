from . import db
from .user import User


class Reaction(db.EmbeddedDocument):
    user = db.LazyReferenceField(User, required=True)
    reaction = db.StringField(required=True, choices=["like", "dislike"])
