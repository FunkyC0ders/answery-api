from graphene import Schema, ObjectType, Field, String, Boolean, ID, List
from graphql import GraphQLError
from werkzeug.security import check_password_hash
from flask_jwt_extended import jwt_required, jwt_refresh_token_required, get_raw_jwt, get_jwt_identity
from .user import SignIn, Signup, User as UserType, SignInInput, UpdateUser, DeleteAvatar
from .auth import Token, create_tokens, blacklist, refresh_access_token
from .question import CreateQuestion, Question as QuestionType, DeleteImg, ReactToQuestion
from .answer import AnswerQuestion, Answer as AnswerType, ReplyToAnswer, Reply as ReplyType, ReactToAnswer, ReactToReply
from .category import Category as CategoryType, AddCategory
from .location import Location as LocationType, AddCountry, AddCity, Country as CountryType
from app.models.user import User as UserModel
from app.models.question import Question as QuestionModel
from app.models.answer import Answer as AnswerModel, Reply as ReplyModel
from app.models.category import Category as CategoryModel
from app.models.location import City as CityModel, Country as CountryModel
import json


class QueryType(ObjectType):
    class Meta:
        name = "Query"
        description = "..."

    # User
    sign_in = Field(SignIn, sign_in_data=SignInInput(required=True), required=True)
    sign_out = Boolean(required=True)
    refresh = Field(Token, required=True)
    avatar = String()

    @staticmethod
    def resolve_sign_in(root, info, sign_in_data):
        user = UserModel.find_by_email(sign_in_data["email"])

        if user and check_password_hash(user.password, sign_in_data["password"]):
            return SignIn(user=user, token=create_tokens(user, sign_in_data.get("remember_me", False)))

        raise GraphQLError("email or password were incorrect")

    @staticmethod
    @jwt_refresh_token_required
    def resolve_sign_out(root, info):
        jti = get_raw_jwt()['jti']
        blacklist.add(jti)
        return True

    @staticmethod
    @jwt_refresh_token_required
    def resolve_refresh(root, info):
        current_user = get_jwt_identity()
        user = UserModel.find_by_id(current_user["id"])
        return refresh_access_token(user)

    @staticmethod
    @jwt_required
    def resolve_avatar(root, info):
        current_user = get_jwt_identity()
        user = UserModel.find_by_id(current_user["id"])
        return user.avatar

    # Question
    question = Field(QuestionType, _id=ID(required=True), required=True)

    @staticmethod
    @jwt_required
    def resolve_question(root, info, _id):
        question = QuestionModel.find_by_id(_id)
        return question

    # Answer
    answer = Field(AnswerType, _id=ID(required=True), required=True)

    @staticmethod
    @jwt_required
    def resolve_answer(root, info, _id):
        answer = AnswerModel.find_by_id(_id)
        return answer

    # Reply
    reply = Field(ReplyType, _id=ID(required=True), required=True)

    @staticmethod
    @jwt_required
    def resolve_reply(root, info, _id):
        reply = ReplyModel.find_by_id(_id)
        return reply

    # Category
    category = Field(CategoryType, _id=ID(required=True), required=True)
    category_list = List(CategoryType, required=True)

    @staticmethod
    @jwt_required
    def resolve_category(root, info, _id):
        category = CategoryModel.find_by_id(_id)
        return category

    @staticmethod
    @jwt_required
    def resolve_category_list(root, info):
        category_list = CategoryModel.find_all()
        return category_list

    # Location
    location = Field(LocationType, _id=ID(required=True), required=True)
    location_list = List(LocationType, required=True)
    country_list = List(CountryType, required=True)
    location_by_country = List(LocationType, country_id=ID(required=True), required=True)

    @staticmethod
    @jwt_required
    def resolve_location(root, info, _id):
        city = CityModel.find_by_id(_id)
        return city.to_location()

    @staticmethod
    @jwt_required
    def resolve_location_list(root, info):
        city_list = CityModel.find_all()
        return [city.to_location() for city in city_list]

    @staticmethod
    @jwt_required
    def resolve_country_list(root, info):
        country_list = CountryModel.find_all()
        return country_list

    @staticmethod
    @jwt_required
    def resolve_location_by_country(root, info, country_id):
        city_list = CityModel.find_by_country(country_id)
        return [city.to_location() for city in city_list]


class MutationType(ObjectType):
    class Meta:
        name = "Mutation"
        description = "..."

    # User
    signup = Signup.Field(required=True)
    update_user = UpdateUser.Field(required=True)
    delete_avatar = DeleteAvatar.Field(required=True)

    # Question
    create_question = CreateQuestion.Field(required=True)
    react_to_question = ReactToQuestion.Field(required=True)
    delete_img = DeleteImg.Field(required=True)

    # Answer
    answer_question = AnswerQuestion.Field(required=True)
    react_to_answer = ReactToAnswer.Field(required=True)

    # Reply
    reply_to_answer = ReplyToAnswer.Field(required=True)
    react_to_reply = ReactToReply.Field(required=True)

    # Category
    add_category = AddCategory.Field(required=True)

    # Location
    add_country = AddCountry.Field(required=True)
    add_ciy = AddCity.Field(required=True)


schema = Schema(query=QueryType, mutation=MutationType)
