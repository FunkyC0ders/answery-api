from graphene import ObjectType, Mutation, InputObjectType, Interface, String, Boolean, Int, DateTime, Field, List


class CommonAttributes(object):
    country = String(required=True)
    city = String(required=True)


class LocationInterface(CommonAttributes, Interface):
    pass


class Location(ObjectType):
    class Meta:
        name = "Location"
        description = "..."
        interfaces = (LocationInterface,)


class LocationInput(CommonAttributes, InputObjectType):
    pass
