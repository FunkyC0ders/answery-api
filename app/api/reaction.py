from graphene import ObjectType, Mutation, InputObjectType, Interface, String, Boolean, Int, DateTime, Field, List
from .user import User


class CommonAttributes(object):
    reaction = String(required=True)


class ReactionInterface(CommonAttributes, Interface):
    user = Field(User, required=True)


class Reaction(ObjectType):
    class Meta:
        name = "Reaction"
        description = "..."
        interfaces = (ReactionInterface,)


class ReactionInput(CommonAttributes, InputObjectType):
    pass
