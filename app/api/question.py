from graphene import ObjectType, Mutation, InputObjectType, Interface, String, ID, Boolean, Int, DateTime, Field, List
from graphql import GraphQLError
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.question import Question as QuestionModel
from app.models.user import User as UserModel
from .user import User
from .location import Location, LocationInput
from .reaction import Reaction
from .answer import Answer
import json


class CommonAttributes(object):
    title = String(required=True)
    content = String()
    images = List(String)
    category = String(required=True)


class QuestionInterface(CommonAttributes, Interface):
    id = ID(required=True)
    created_by = Field(User, required=True)
    approved = Boolean(required=True)
    creation_date = DateTime(required=True)
    view_count = Int(required=True)
    location = Field(Location, required=True)
    reactions = Field(Reaction)
    answers = List(Answer)


class Question(ObjectType):
    class Meta:
        name = "Question"
        description = "..."
        interfaces = (QuestionInterface,)


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
        user = UserModel.find_by_id(current_user["id"])
        if not user:
            errors["user"] = "not found"

        if errors:
            raise GraphQLError(json.dumps(errors))

        question = QuestionModel(created_by=user, **question_data)
        question.save()

        return CreateQuestion(question=question)
