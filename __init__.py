from flask_restx import Api
from user import api as user_api
from item import api as item_api
from store import api as store_api
from flask_restx.marshalling import marshal
from base import Base,engine,Session
from flask import Flask


app = Flask(__name__)
api = Api(
    title="E-Store API",
    version="1.0",
    description="A simple e-store API.<br> For manage users,stores,items.",
)

Base.metadata.create_all(engine)
session=Session() 

api.add_namespace(user_api)
api.add_namespace(item_api)
api.add_namespace(store_api)


if __name__=='__main__':
    app.run(debug=True)