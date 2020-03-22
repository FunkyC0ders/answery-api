from graphene import ObjectType, Mutation, InputObjectType, Interface, String, ID, Boolean, Int, DateTime, Field, List
from graphql import GraphQLError
from flask_jwt_extended import jwt_required, get_jwt_identity
from .user import User
from .location import Location
from .reaction import Reaction
from .answer import Answer
from .category import Category
from app.models.question import Question as QuestionModel
from app.models.user import User as UserModel
from app.models.category import Category as CategoryModel
from app.models.location import Location as LocationModel
import json


class CommonAttributes(object):
    title = String(required=True)
    content = String()
    images = List(String)


class QuestionInterface(CommonAttributes, Interface):
    id = ID(required=True)
    created_by = Field(User, required=True)
    approved = Boolean(required=True)
    creation_date = DateTime(required=True)
    view_count = Int(required=True)
    location = Field(Location, required=True)
    category = Field(Category, required=True)
    reactions = Field(Reaction)
    answers = List(Answer)


class Question(ObjectType):
    class Meta:
        name = "Question"
        description = "..."
        interfaces = (QuestionInterface,)


class NewQuestion(CommonAttributes, InputObjectType):
    location_id = ID(required=True)
    category_id = ID(required=True)


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

        category = CategoryModel.find_by_id(question_data["category_id"])
        if not category:
            errors["category"] = "not found"

        location = LocationModel.find_by_id(question_data["location_id"])
        if not location:
            errors["location"] = "not found"

        if errors:
            raise GraphQLError(json.dumps(errors))

        del question_data["category_id"]
        del question_data["location_id"]
        question = QuestionModel(created_by=user, category=category, location=location, **question_data)
        question.save()

        return CreateQuestion(question=question)
