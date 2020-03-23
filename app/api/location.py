from graphene import ObjectType, Mutation, InputObjectType, Interface, String, ID, Boolean, Int, DateTime, Field, List
from graphql import GraphQLError
from flask_jwt_extended import jwt_required
from .translation import Translation, NewTranslation
from app.models.location import City as CityModel, Country as CountryModel
import json


class CommonAttributes(object):
    pass


class CountryInterface(Interface):
    id = ID(required=True)
    name = List(Translation, required=True)


class Country(ObjectType):
    class Meta:
        name = "Country"
        description = "..."
        interfaces = (CountryInterface,)


class CityInterface(Interface):
    id = ID(required=True)
    name = List(Translation, required=True)
    country = Field(Country, required=True)


class City(ObjectType):
    class Meta:
        name = "City"
        description = "..."
        interfaces = (CityInterface,)


class LocationInterface(CommonAttributes, Interface):
    id = ID(required=True)
    country = List(Translation, required=True)
    city = List(Translation, required=True)


class Location(ObjectType):
    class Meta:
        name = "Location"
        description = "..."
        interfaces = (LocationInterface,)


class NewCountry(CommonAttributes, InputObjectType):
    name = List(NewTranslation, required=True)


class AddCountry(Mutation):
    class Meta:
        name = "AddCountry"
        description = "..."

    class Arguments:
        country_data = NewCountry(required=True)

    country = Field(lambda: Country, required=True)

    @staticmethod
    @jwt_required
    def mutate(root, info, country_data):
        errors = {}

        country = CountryModel(**country_data)
        country.save()

        return AddCountry(country=country)


class NewCity(CommonAttributes, InputObjectType):
    name = List(NewTranslation, required=True)
    country_id = ID(required=True)


class AddCity(Mutation):
    class Meta:
        name = "AddCity"
        description = "..."

    class Arguments:
        city_data = NewCity(required=True)

    city = Field(lambda: City, required=True)
    location = Field(lambda: Location, required=True)

    @staticmethod
    @jwt_required
    def mutate(root, info, city_data):
        errors = {}

        country = CountryModel.find_by_id(city_data["country_id"])
        if not country:
            errors["country"] = "not found"

        if errors:
            raise GraphQLError(json.dumps(errors))

        del city_data["country_id"]

        city = CityModel(country=country, **city_data)
        city.save()

        return AddCity(city=city, location=city.to_location())
