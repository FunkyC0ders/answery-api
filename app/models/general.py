from . import db


class Translation(db.EmbeddedDocument):
    language = db.StringField(required=True)
    text = db.StringField(required=True)


class Reaction(db.EmbeddedDocument):
    user = db.LazyReferenceField("User", required=True)
    reaction = db.StringField(required=True, choices=["like", "dislike"])
