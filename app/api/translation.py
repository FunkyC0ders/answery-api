from graphene import ObjectType, Mutation, InputObjectType, Interface, String, ID, Boolean, Int, DateTime, Field, List
from graphql import GraphQLError
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.general import Translation as TranslationModel


class CommonAttributes(object):
    language = String(required=True)
    text = String(required=True)


class TranslationInterface(CommonAttributes, Interface):
    pass


class Translation(ObjectType):
    class Meta:
        name = "Translation"
        description = "..."
        interfaces = (TranslationInterface,)


class NewTranslation(CommonAttributes, InputObjectType):
    pass
