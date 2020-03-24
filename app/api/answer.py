from graphene import ObjectType, Mutation, InputObjectType, Interface, String, ID, Boolean, Int, DateTime, Field, List
from graphql import GraphQLError
from flask_jwt_extended import jwt_required, get_jwt_identity
from .user import User
from .reaction import Reaction, ReactionInput
from app.models.user import User as UserModel
from app.models.question import Question as QuestionModel
from app.models.answer import Answer as AnswerModel, Reply as ReplyModel
from app.models.general import Reaction as ReactionModel
import json


class CommonAttributes(object):
    content = String(required=True)


class ReplyInterface(CommonAttributes, Interface):
    id = ID(required=True)
    created_by = Field(User, required=True)
    creation_date = DateTime(required=True)
    reactions = List(Reaction, required=True)


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

    ok = Boolean(required=True)
    reply = Field(lambda: Reply, required=True)

    @staticmethod
    @jwt_required
    def mutate(root, info, answer_id, reply_data):
        errors = {}

        current_user = get_jwt_identity()
        user = UserModel.find_by_id(current_user["id"])
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

        return ReplyToAnswer(reply=reply, ok=True)


class AnswerQuestion(Mutation):
    class Meta:
        name = "AnswerQuestion"
        description = "..."

    class Arguments:
        question_id = ID(required=True)
        answer_data = NewAnswer(required=True)

    ok = Boolean(required=True)
    answer = Field(lambda: Answer, required=True)

    @staticmethod
    @jwt_required
    def mutate(root, info, question_id, answer_data):
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

        answer = AnswerModel(created_by=user, **answer_data)
        answer.save()

        if question.answers:
            question.answers.append(answer)
        else:
            question.answers = [answer]

        question.save()

        return AnswerQuestion(answer=answer, ok=True)


class ReactToReply(Mutation):
    class Meta:
        name = "ReactToReply"
        description = "..."

    class Arguments:
        reply_id = ID(required=True)
        reaction_data = ReactionInput(required=True)

    ok = Boolean(required=True)
    reply = Field(lambda: Reply, required=True)
    reactions = List(lambda: Reaction, required=True)

    @staticmethod
    @jwt_required
    def mutate(root, info, reply_id, reaction_data):
        errors = {}

        current_user = get_jwt_identity()
        user = UserModel.find_by_id(current_user["id"])
        if not user:
            errors["user"] = "not found"

        reply = ReplyModel.find_by_id(reply_id)
        if not reply:
            errors["reply"] = "not found"

        if errors:
            raise GraphQLError(json.dumps(errors))

        reaction = ReactionModel(user=user, **reaction_data)

        if not reply.reactions:
            reply.reactions = [reaction]

        else:
            old_reaction = list(filter(lambda r: r.user == reaction.user, reply.reactions))
            if old_reaction:
                if old_reaction[0].reaction != reaction.reaction:
                    reply.reactions.remove(old_reaction[0])
                    reply.reactions.append(reaction)
            else:
                reply.reactions.append(reaction)

        reply.save()
        return ReactToReply(reply=reply, reactions=reply.reactions, ok=True)


class ReactToAnswer(Mutation):
    class Meta:
        name = "ReactToAnswer"
        description = "..."

    class Arguments:
        answer_id = ID(required=True)
        reaction_data = ReactionInput(required=True)

    ok = Boolean(required=True)
    answer = Field(lambda: Answer, required=True)
    reactions = List(lambda: Reaction, required=True)

    @staticmethod
    @jwt_required
    def mutate(root, info, answer_id, reaction_data):
        errors = {}

        current_user = get_jwt_identity()
        user = UserModel.find_by_id(current_user["id"])
        if not user:
            errors["user"] = "not found"

        answer = AnswerModel.find_by_id(answer_id)
        if not answer:
            errors["answer"] = "not found"

        if errors:
            raise GraphQLError(json.dumps(errors))

        reaction = ReactionModel(user=user, **reaction_data)

        if not answer.reactions:
            answer.reactions = [reaction]

        else:
            old_reaction = list(filter(lambda r: r.user == reaction.user, answer.reactions))
            if old_reaction:
                if old_reaction[0].reaction != reaction.reaction:
                    answer.reactions.remove(old_reaction[0])
                    answer.reactions.append(reaction)
            else:
                answer.reactions.append(reaction)

        answer.save()
        return ReactToAnswer(answer=answer, reactions=answer.reactions, ok=True)
