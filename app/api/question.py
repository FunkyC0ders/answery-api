from graphene import ObjectType, Mutation, InputObjectType, Interface, String, Boolean, Int, DateTime, Field, List
from graphql import GraphQLError
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.question import Question as QuestionModel
from app.models.user import User as UserModel
from .user import User
import json


class LocationAttributes(object):
    country = String(required=True)
    city = String(required=True)


class Location(LocationAttributes, ObjectType):
    pass


class CommonAttributes(object):
    title = String(required=True)
    content = String()
    images = List(String)
    category = String(required=True)


class QuestionInterface(CommonAttributes, Interface):
    created_by = Field(User, required=True)
    approved = Boolean(required=True)
    creation_date = DateTime(required=True)
    view_count = Int(required=True)
    location = Field(Location, required=True)
    reactions = None  # TODO fill this
    answers = None  # TODO fill this


class Question(ObjectType):
    class Meta:
        name = "Question"
        description = "..."
        interfaces = (QuestionInterface,)


class LocationInput(LocationAttributes, InputObjectType):
    pass


class NewQuestion(CommonAttributes, InputObjectType):
    location = LocationInput(required=True)


class CreateQuestion(Mutation):
    class Meta:
        name = "CreateQuestion"
        description = "..."

    class Arguments:
        question_data = NewQuestion(required=True)

    question = Field(lambda: Question, required=True)

    @staticmethod
    @jwt_required
    def mutate(root, info, question_data):
        errors = {}

        current_user = get_jwt_identity()

        user = UserModel.find_by_id(current_user["_id"])

        question = QuestionModel(created_by=user, **question_data)
        question.save()

        return CreateQuestion(question=question)
