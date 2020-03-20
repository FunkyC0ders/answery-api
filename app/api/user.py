from graphene import ObjectType, Mutation, InputObjectType, Interface, String, Boolean, Field, DateTime
from graphql import GraphQLError
from werkzeug.security import generate_password_hash
from .auth import Token, create_tokens
from app.models.user import User as UserModel
import json


class CommonAttributes(object):
    name = String(required=True)
    email = String(required=True)
    avatar = String()


class UserInterface(CommonAttributes, Interface):
    creation_date = DateTime(required=True)
    verified = Boolean(required=True)


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


class NewUser(CommonAttributes, InputObjectType):
    password = String(required=True)


class EditUser(InputObjectType):
    name = String()
    email = String()
    avatar = String()


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
