# App
from flask import Flask

app = Flask(__name__)

app.config["HOST"] = "localhost"
app.config["PORT"] = 5000
app.config["DEBUG"] = True

# Cross-Origin Resource Sharing
from flask_cors import CORS

CORS(app)


# JWT
from flask_jwt_extended import JWTManager

app.config['JWT_SECRET_KEY'] = 'g07USLZd3WzytP-62w8CmVAJaXtW7v0galtJsH4UVgY'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)


# Database
from .models import db, DB_HOST, DB_NAME, DB_PORT

app.config["MONGODB_DB"] = DB_NAME
app.config["MONGODB_HOST"] = DB_HOST
app.config["MONGODB_PORT"] = DB_PORT
db.init_app(app)

# GraphQL
from flask_graphql import GraphQLView
from app.api import schema
from app.api.auth import user_identity_lookup, add_claims_to_access_token

app.add_url_rule('/api', view_func=GraphQLView.as_view('api', schema=schema, graphiql=True))


# URL
from app.web import web

app.register_blueprint(web)
