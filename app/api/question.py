from graphene import ObjectType, Mutation, InputObjectType, Interface, String, ID, Boolean, Int, DateTime, Field, List
from graphql import GraphQLError
from flask import url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from .user import User
from .location import Location
from .reaction import Reaction, ReactionInput
from .answer import Answer
from .category import Category
from app.models.question import Question as QuestionModel
from app.models.user import User as UserModel
from app.models.category import Category as CategoryModel
from app.models.location import City as CityModel
from app.models.general import Reaction as ReactionModel
from app.web import ROOT_PATH
import json
import os


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
    reactions = List(Reaction)
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

    ok = Boolean(required=True)
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

        location = CityModel.find_by_id(question_data["location_id"])
        if not location:
            errors["location"] = "not found"

        if errors:
            raise GraphQLError(json.dumps(errors))

        del question_data["category_id"]
        del question_data["location_id"]
        question = QuestionModel(created_by=user, category=category, location=location, **question_data)
        question.save()

        return CreateQuestion(question=question, ok=True)


class DeleteImg(Mutation):
    class Meta:
        name = "DeleteImg"
        description = "..."

    class Arguments:
        question_id = ID(required=True)
        file_name = String(required=True)

    ok = Boolean(required=True)
    question = Field(lambda: Question, required=True)

    @staticmethod
    @jwt_required
    def mutate(root, info, question_id, file_name):
        errors = {}

        current_user = get_jwt_identity()
        user = UserModel.find_by_id(current_user["id"])
        if not user:
            errors["user"] = "not found"

        question = QuestionModel.find_by_id(question_id)
        if not question:
            errors["question"] = "not found"

        if user != question.created_by:
            errors["user"] = "do not have permission to edit this question"

        if file_name not in question.images:
            errors["question"] = "does not have an image called {}".format(file_name)

        if errors:
            raise GraphQLError(json.dumps(errors))

        file_path = ROOT_PATH + url_for("static", filename="img/{}".format(file_name))
        os.remove(file_path)

        question.images.remove(file_name)
        question.save()

        return DeleteImg(question=question, ok=True)


class ReactToQuestion(Mutation):
    class Meta:
        name = "AddReaction"
        description = "..."

    class Arguments:
        question_id = ID(required=True)
        reaction_data = ReactionInput(required=True)

    ok = Boolean(required=True)
    question = Field(lambda: Question, required=True)
    reactions = List(lambda: Reaction, required=True)

    @staticmethod
    @jwt_required
    def mutate(root, info, question_id, reaction_data):
        errors = {}

        current_user = get_jwt_identity()
        user = UserModel.find_by_id(current_user["id"])
        if not user:
            errors["user"] = "not found"

        question = QuestionModel.find_by_id(question_id)
        if not question:
            errors["question"] = "not found"

        if errors:
            raise GraphQLError(json.dumps(errors))

        reaction = ReactionModel(user=user, **reaction_data)

        if not question.reactions:
            question.reactions = [reaction]

        else:
            old_reaction = list(filter(lambda r: r.user == reaction.user, question.reactions))
            if old_reaction:
                if old_reaction[0].reaction != reaction.reaction:
                    question.reactions.remove(old_reaction[0])
                    question.reactions.append(reaction)
            else:
                question.reactions.append(reaction)

        question.save()
        return ReactToQuestion(question=question, reactions=question.reactions, ok=True)
