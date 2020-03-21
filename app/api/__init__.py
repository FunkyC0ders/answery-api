from graphene import Schema, ObjectType, Field, String, Boolean, ID
from graphql import GraphQLError
from werkzeug.security import check_password_hash
from flask_jwt_extended import jwt_required, jwt_refresh_token_required, get_raw_jwt, get_jwt_identity
from .user import SignIn, Signup, User as UserType
from .auth import Token, create_tokens, blacklist, refresh_access_token
from .question import CreateQuestion, Question as QuestionType
from .answer import AnswerQuestion, Answer as AnswerType, ReplyToAnswer, Reply as ReplyType
from app.models.user import User as UserModel
from app.models.question import Question as QuestionModel
from app.models.answer import Answer as AnswerModel, Reply as ReplyModel
import json


class QueryType(ObjectType):
    class Meta:
        name = "Query"
        description = "..."

    # User
    sign_in = Field(SignIn,
                    email=String(required=True),
                    password=String(required=True),
                    required=True)
    sign_out = Boolean(required=True)
    refresh = Field(Token, required=True)
    avatar = String()

    @staticmethod
    def resolve_sign_in(root, info, email, password, remember_me=False):
        user = UserModel.find_by_email(email)

        if user and check_password_hash(user.password, password):
            return SignIn(user=user, token=create_tokens(user, remember_me))

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
        user = UserModel.find_by_id(current_user["_id"])
        return refresh_access_token(user)

    @staticmethod
    @jwt_required
    def resolve_avatar(root, info):
        current_user = get_jwt_identity()
        user = UserModel.find_by_id(current_user._id)
        return user.avatar

    # Question
    question = Field(QuestionType, _id=ID(required=True), required=True)

    @staticmethod
    @jwt_required
    def resolve_question(root, info, _id):
        question = QuestionModel.find_by_id(_id)
        return question

    # Answer
    answer = Field(AnswerType, _id=ID(), required=True)

    @staticmethod
    @jwt_required
    def resolve_answer(root, info, _id):
        answer = AnswerModel.find_by_id(_id)
        return answer

    # Reply
    reply = Field(ReplyType, _id=ID(), required=True)

    @staticmethod
    @jwt_required
    def resolve_reply(root, info, _id):
        reply = ReplyModel.find_by_id(_id)
        return reply


class MutationType(ObjectType):
    class Meta:
        name = "Mutation"
        description = "..."

    # User
    signup = Signup.Field(required=True)

    # Question
    create_question = CreateQuestion.Field(required=True)

    # Answer
    answer_question = AnswerQuestion.Field(required=True)

    # Reply
    reply_to_answer = ReplyToAnswer.Field(required=True)


schema = Schema(query=QueryType, mutation=MutationType)
