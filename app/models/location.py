from flask_mongoengine import Document
from . import db
from .general import Translation


class Country(Document):
    meta = {"collection": "countries"}

    name = db.EmbeddedDocumentListField(Translation, required=True, unique=True)

    @classmethod
    def find_by_id(cls, _id):
        return cls.objects(id=_id).first()

    @classmethod
    def find_all(cls):
        return cls.objects()


class City(Document):
    meta = {"collection": "cities"}

    name = db.EmbeddedDocumentListField(Translation, required=True, unique_with=["country"])
    country = db.ReferenceField(Country, required=True, reverse_delete_rule=2)

    def to_location(self):
        return dict(id=self.id, city=self.name, country=self.country.name)

    @classmethod
    def find_by_id(cls, _id):
        return cls.objects(id=_id).first()

    @classmethod
    def find_all(cls):
        return cls.objects()

    @classmethod
    def find_by_country(cls, country_id):
        return cls.objects(country=country_id)
