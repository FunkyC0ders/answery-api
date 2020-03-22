from graphene import ObjectType, Mutation, InputObjectType, Interface, String, ID, Boolean, Int, DateTime, Field, List
from graphql import GraphQLError
from flask_jwt_extended import jwt_required
from .translation import Translation, NewTranslation
from app.models.location import Location as LocationModel


class CommonAttributes(object):
    pass


class LocationInterface(CommonAttributes, Interface):
    id = ID(required=True)
    country = List(Translation, required=True)
    city = List(Translation, required=True)


class Location(ObjectType):
    class Meta:
        name = "Location"
        description = "..."
        interfaces = (LocationInterface,)


class NewLocation(CommonAttributes, InputObjectType):
    country = List(NewTranslation, required=True)
    city = List(NewTranslation, required=True)


class AddLocation(Mutation):
    class Meta:
        name = "AddLocation"
        description = "..."

    class Arguments:
        location_data = NewLocation(required=True)

    location = Field(lambda: Location, required=True)

    @staticmethod
    @jwt_required
    def mutate(root, info, location_data):
        errors = {}

        location = LocationModel(**location_data)
        location.save()

        return AddLocation(location=location)
