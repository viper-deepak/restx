from flask_restx.marshalling import marshal
from flask import Flask,request,session
from flask_restx import Api, Resource,fields,reqparse
from base import Base,engine,Session
from sqlalchemy.ext.declarative import declarative_base
from model import StoreModel,ItemModel,UserModel

app=Flask(__name__)
api=Api(app,doc='/',title="A Store API",description="A REST API for Store")


app.secret_key = "a1b2c"

Base.metadata.create_all(engine)
session=Session() 


_item_list = api.model('_item_list', {
    'id': fields.Integer(
        readonly=True,
        description="The user identifier"
    ),
    'name': fields.String(
        required=True,
        description="The item name"
    ),
    'price': fields.Float(
        required=True,
        description="The item price"
    ),
})

_store_list = api.model('_store_list', {
    'id': fields.Integer(
        readonly=True,
        description="The user identifier"
    ),
    'name': fields.String(
        required=True,
        description="The store name"
    ),
    'items': fields.List(
        fields.Nested(_item_list),
        description="The store's item"
    ),
})

_user_list = api.model('_user_list', {
    'id': fields.Integer(readonly=True, description="The user identifier"),
    'username': fields.String(required=True, description="The user name"),
})
_user_create = api.model('_user_create', {
    'username': fields.String(required=True, description="The username"),
    'password': fields.String(required=True, description="The user password"),
})

_item_create = api.model('_item_create', {
    'name': fields.String(required=True, description="The item name"),
    'price': fields.Float(required=True, description="The item price"),
    'store_id': fields.Integer(required=True, description="belong which store"),
})
_item_list = api.model('_item_list', {
    'id': fields.Integer(),
    'name': fields.String(),
    'price': fields.Float(),
    'store_id': fields.Integer(),
})




@api.route('/store')
class StoreList(Resource):
    @api.marshal_list_with(_store_list)
    def get(self):
        """list all stores"""
        store=session.query(StoreModel).all()
        if not store:
            api.abort(404)
            return
        return session.query(StoreModel).all()

    @api.response(201, 'Success')
    @api.response(400, 'store name already exists')
    def post(self):
        """create a store"""
        data=request.get_json()
        name =data.get('name')
        try:
            new_store=StoreModel(name)
            session.add(new_store)
            session.commit()
        except:
            return {"message": "An error occurred while creating the store."}, 500

        return marshal(new_store, _store_list), 201



@api.route('/store/<name>')
class Store(Resource):
    @api.response(404, 'Store not found.')
    @api.marshal_with(_store_list)
    def get(self, name):
        """get a store"""
        store = session.query(StoreModel).filter(StoreModel.name==name).first()
        if store:
            return store
        api.abort(404)
        return


    def delete(self, name):
        """delete store"""
        store_to_delete=session.query(StoreModel).filter(StoreModel.name==name).first()
        session.delete(store_to_delete)
        session.commit()
        return {'message': 'Store deleted'}


@api.route('/user/register')
@api.response(201, "User created successfully")
@api.response(400, "that username already exists.")
class UserRegister(Resource):
    @api.doc("register user")
    @api.expect(_user_create)
    @api.marshal_with(_user_list)
    def post(self):
        """register a user"""
        data = request.get_json()
        username =data.get('username')
        password =data.get('password')
        if session.query(UserModel).filter(UserModel.username==username).first():
            api.abort(400, 'that username already exists.')
            return

        user = UserModel(username,password)
        session.add(user)
        session.commit()
        return user, 201



@api.route('/user/')
class UserList(Resource):
    @api.doc("list_users")
    @api.marshal_list_with(_user_list, envelope='data')
    def get(self):
        """list all user"""
        user = session.query(UserModel).all()
        if not user:
            api.abort(404)
            return
        return user, 200


@api.route('/user/<int:user_id>')
@api.param("user_id", "The user identifier")
@api.response(404, "User not found")
class User(Resource):
    @api.marshal_with(_user_list)
    def get(self, user_id):
        """get a user"""
        user = session.query(UserModel).get(user_id)
        if not user:
            api.abort(404, "User not found")
            return
        return user, 200

    @api.response(200, "User deleted.")
    def delete(self, user_id):
        """Delete user"""
        user = session.query(UserModel).filter(UserModel.id==user_id).first()
        if not user:
            api.abort(404, 'User not found')
            return
        session.delete(user)
        session.commit()
        return {'message': 'User deleted.'}, 200


@api.route('/item/<int:item_id>')
class Item(Resource):
    

    @api.doc(security='apikey')
    @api.marshal_with(_item_list)
    @api.response(404, 'Item not found')
    def get(self, item_id):
        """get item by name"""
        item = session.query(ItemModel).filter(ItemModel.id==item_id).first()
        if item:
            return item
        api.abort(404, 'Item not found')
        return

   

    @api.doc(security='apikey')
    def delete(self, item_id):
        """delete item"""
        
        item = session.query(ItemModel).filter(ItemModel.id==item_id).first()
        if item:
            session.delete(item)
            session.commit()

        return {'message': 'Item deleted'}

    @api.doc(security='apikey')
    @api.marshal_with(_item_list)
    def put(self, item_id):
        """update item"""
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')
        item_to_update=session.query(ItemModel).get(item_id)
        item_to_update.price = price
        session.commit()
        return item_to_update



@api.route('/item/')
class ItemList(Resource):
    @api.doc(security='apikey')
    @api.marshal_list_with(_item_list)
    def get(self):
        """list all item"""

        all_items = session.query(ItemModel).all()
        if not all_items:
            api.abort(404)
            return
        return all_items, 200

    @api.doc(security='apikey')
    @api.expect(_item_create)
    def post(self):
        """create a item"""
        
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')
        store_id = data.get('store_id')
        if session.query(ItemModel).filter(ItemModel.name==name).first():
            return {'message': "An item with name '{}' already exists.".format(name)}, 400
        item = ItemModel(name,price,store_id)
        try:
            session.add(item)
            session.commit()
        except:
            return {"message": "An error occurred inserting the item."}, 500
        return marshal(item, _item_list), 201




if __name__ == "__main__":
    app.run(debug=True)