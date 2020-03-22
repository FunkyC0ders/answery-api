from graphene import ObjectType, Mutation, InputObjectType, Interface, String, Boolean, Field, DateTime
from graphql import GraphQLError
from flask import url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from .auth import Token, create_tokens
from app.models.user import User as UserModel
from app.web import ROOT_PATH
import json
import os


class CommonAttributes(object):
    name = String(required=True)
    email = String(required=True)
    # avatar = String()


class UserInterface(CommonAttributes, Interface):
    creation_date = DateTime(required=True)
    verified = Boolean(required=True)
    avatar = String()


class User(ObjectType):
    class Meta:
        name = "User"
        description = "..."
        interfaces = (UserInterface,)


class SignIn(ObjectType):
    class Meta:
        name = "SignIn"
        description = "..."

    user = Field(User, required=True)
    token = Field(Token, required=True)


class SignInInput(InputObjectType):
    email = String(required=True)
    password = String(required=True)
    remember_my = Boolean()


class NewUser(CommonAttributes, InputObjectType):
    password = String(required=True)


class EditUser(InputObjectType):
    name = String()
    email = String()
    # avatar = String()


class Signup(Mutation):
    class Meta:
        name = "Signup"
        description = "..."

    class Arguments:
        user_data = NewUser(required=True)

    user = Field(lambda: User, required=True)
    token = Field(lambda: Token, required=True)

    @staticmethod
    def mutate(root, info, user_data):
        errors = {}

        email_check = UserModel.find_by_email(user_data.email)
        if email_check:
            errors["email"] = "This email already exists."

        if errors:
            raise GraphQLError(json.dumps(errors))

        user = UserModel(**user_data)
        user.password = generate_password_hash(user_data.password, method="sha256")

        user.save()
        return Signup(user=user, token=create_tokens(user))


class UpdateUser(Mutation):
    class Meta:
        name = "UpdateUser"
        description = "..."

    class Arguments:
        user_data = EditUser(required=True)

    user = Field(lambda: User, required=True)

    @staticmethod
    @jwt_required
    def mutate(root, info, user_data):
        errors = {}

        current_user = get_jwt_identity()
        user = UserModel.find_by_id(current_user["id"])
        if not user:
            errors["user"] = "not found"

        if "email" in user_data.keys():
            print(user_data["email"])
            email_check = UserModel.find_by_email(user_data["email"])
            if email_check and email_check != user:
                errors["email"] = "already exists"

        if errors:
            raise GraphQLError(json.dumps(errors))

        for key in user_data.keys():
            setattr(user, key, user_data[key])

        user.save()

        return UpdateUser(user=user)


class DeleteAvatar(Mutation):
    class Meta:
        name = "DeleteAvatar"
        description = "..."

    class Arguments:
        pass

    user = Field(lambda: User, required=True)

    @staticmethod
    @jwt_required
    def mutate(root, info):
        errors = {}

        current_user = get_jwt_identity()
        user = UserModel.find_by_id(current_user["id"])
        if not user:
            errors["user"] = "not found"

        if not user.avatar:
            errors["avatar"] = "not found"

        if errors:
            raise GraphQLError(json.dumps(errors))

        file_path = ROOT_PATH + url_for("static", filename="avatar/{}".format(user.avatar))
        os.remove(file_path)

        user.avatar = None
        user.save()

        return DeleteAvatar(user=user)
