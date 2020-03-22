from graphene import ObjectType, Mutation, InputObjectType, Interface, String, ID, Boolean, Int, DateTime, Field, List
from graphql import GraphQLError
from flask_jwt_extended import jwt_required, get_jwt_identity
from .translation import Translation, NewTranslation
from app.models.category import Category as CategoryModel


class CommonAttributes(object):
    pass


class CategoryInterface(CommonAttributes, Interface):
    id = ID(required=True)
    name = List(Translation, required=True)


class Category(ObjectType):
    class Meta:
        name = "Category"
        description = "..."
        interfaces = (CategoryInterface,)


class NewCategory(CommonAttributes, InputObjectType):
    name = List(NewTranslation, required=True)


class AddCategory(Mutation):
    class Meta:
        name = "AddCategory"
        description = "..."

    class Arguments:
        category_data = NewCategory(required=True)

    category = Field(lambda: Category, required=True)

    @staticmethod
    @jwt_required
    def mutate(root, info, category_data):
        errors = {}

        category = CategoryModel(**category_data)
        category.save()

        return AddCategory(category=category)
