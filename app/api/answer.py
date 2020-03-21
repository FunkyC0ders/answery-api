from graphene import ObjectType, Mutation, InputObjectType, Interface, String, ID, Boolean, Int, DateTime, Field, List
from graphql import GraphQLError
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User as UserModel
from app.models.question import Question as QuestionModel
from app.models.answer import Answer as AnswerModel, Reply as ReplyModel
from .user import User
from .reaction import Reaction
import json


class CommonAttributes(object):
    content = String(required=True)


class ReplyInterface(CommonAttributes, Interface):
    id = ID(required=True)
    created_by = Field(User, required=True)
    creation_date = DateTime(required=True)
    reactions = Field(Reaction, required=True)


class Reply(ObjectType):
    class Meta:
        name = "Reply"
        description = "..."
        interfaces = (ReplyInterface,)


class Answer(ObjectType):
    class Meta:
        name = "Answer"
        description = "..."
        interfaces = (ReplyInterface,)

    replies = List(Reply)


class NewReply(CommonAttributes, InputObjectType):
    pass


class NewAnswer(CommonAttributes, InputObjectType):
    pass


class ReplyToAnswer(Mutation):
    class Meta:
        name = "ReplyToAnswer"
        description = "..."

    class Arguments:
        answer_id = ID(required=True)
        reply_data = NewReply(required=True)

    reply = Field(lambda: Reply, required=True)

    @staticmethod
    @jwt_required
    def mutate(root, info, answer_id, reply_data):
        errors = {}

        current_user = get_jwt_identity()
        user = UserModel.find_by_id(current_user["_id"])
        if not user:
            errors["user"] = "not found"

        answer = AnswerModel.find_by_id(answer_id)
        if not answer:
            errors["answer"] = "not found"

        if errors:
            raise GraphQLError(json.dumps(errors))

        reply = ReplyModel(created_by=user, **reply_data)
        reply.save()

        if answer.replies:
            answer.replies.append(reply)
        else:
            answer.replies = [reply]

        answer.save()

        return ReplyToAnswer(reply=reply)


class AnswerQuestion(Mutation):
    class Meta:
        name = "AnswerQuestion"
        description = "..."

    class Arguments:
        question_id = ID(required=True)
        answer_data = NewAnswer(required=True)

    answer = Field(lambda: Answer, required=True)

    @staticmethod
    @jwt_required
    def mutate(root, info, question_id, answer_data):
        errors = {}

        current_user = get_jwt_identity()
        user = UserModel.find_by_id(current_user["_id"])
        if not user:
            errors["user"] = "not found"

        question = QuestionModel.find_by_id(question_id)
        if not question:
            errors["question"] = "not found"

        if errors:
            raise GraphQLError(json.dumps(errors))

        answer = AnswerModel(created_by=user, **answer_data)
        answer.save()

        if question.answers:
            question.answers.append(answer)
        else:
            question.answers = [answer]

        question.save()

        return AnswerQuestion(answer=answer)
