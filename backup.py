from flask_restx.marshalling import marshal
from flask import Flask,request,session,jsonify
from flask_restx import Api, Resource,fields
from base import Base,engine,Session
from model import OrderModel, StoreModel,ItemModel,UserModel
import datetime
from werkzeug.security import safe_str_cmp
from blacklist import BLACKLIST
from flask_jwt_extended import create_access_token,create_refresh_token,jwt_required,get_jwt,JWTManager
import os
from config import config

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

app=Flask(__name__)
api=Api(app,doc='/',title="A Store API",authorizations=authorizations,description="A REST API for Store")

app.config["JWT_SECRET_KEY"] = "super-secret"
Base.metadata.create_all(engine)
session=Session() 

jwt = JWTManager(app)

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

_user_order_list = api.model('_user_order_list',{
    'id': fields.Integer(),
    'item_name': fields.Integer(),
    'store_name' : fields.Integer(),
    'order_date' : fields.DateTime(),
})

_user_order = api.model('_user_order',{
    'id': fields.Integer(readonly=True, description="The user identifier"),
    'username': fields.String(required=True, description="The user name"),
    'orders': fields.List(
        fields.Nested(_user_order_list),
        description="The user's order"
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

_order_create = api.model('_order_create', {
    'user_id': fields.Integer(),
    'item_id': fields.Integer(),
    'store_id' : fields.Integer(),
    'order_date' : fields.DateTime(),
})
_order_list = api.model('_order_list', {
    'id': fields.Integer(),
    'user_id': fields.Integer(),
    'item_id': fields.Integer(),
    'store_id' : fields.Integer(),
    'order_date' : fields.DateTime(),
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
        return store

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


@api.route('/store/<int:store_id>')
class StoreItemList(Resource):
    @api.response(404, 'Store not found.')
    @api.marshal_with(_store_list)
    def get(self, store_id):
        """get a store"""
        store = session.query(StoreModel).get(store_id)
        if store:
            return store
        api.abort(404)
        return

    def delete(self, store_id):
        """delete store"""
        store_to_delete=session.query(StoreModel).get(store_id)
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


@api.route('/user')
class UserList(Resource):
    @jwt_required()
    @api.doc("list_users")
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
    @jwt_required()
    @api.marshal_list_with(_user_list)
    def get(self, user_id):
        """get a user"""
        user = session.query(UserModel).get(user_id)
        if not user:
            api.abort(404, "User not found")
            return
        return user, 200

    @jwt_required()
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


@api.route('/view_order/<int:user_id>')
@api.param("user_id", "The user identifier")
@api.response(404, "User,s order not found")
class UserOrderView(Resource):
    @jwt_required()
    @api.marshal_list_with(_user_order)
    def get(self, user_id):
        """get a user's order"""
        user = session.query(UserModel).get(user_id)
        if not user:
            api.abort(404, "User not found")
            return
        return user, 200


@api.route('/login')
@api.response(401, "Invalid Credentials!")
@api.response(200, "Success")
class UserLogin(Resource):
    @api.expect(_user_create)
    def post(self):
        """user login"""
        data = request.get_json()
        username = data.get('username')
        user = session.query(UserModel).filter(UserModel.username==username).first()
        password = data.get('password')
        if user and safe_str_cmp(user.password,password ):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        return {"message": "Invalid Credentials!"}, 401


@api.route('/logout')
class UserLogout(Resource):
    @api.doc(security='apikey')
    @jwt_required()
    def post(self):
        """logout"""
        jti = get_jwt()["jti"]
        BLACKLIST.add(jti)
        return {
            'message': 'Successfuly Logged out.'
        }, 200


@api.route('/refresh')
class TokenRefresh(Resource):
    @api.doc(security='apikey')
    @jwt_required(refresh=True)
    def post(self):
        """refresh access_token"""
        current_user = get_jwt()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}


@api.route('/item/<int:item_id>')
class Item(Resource):
    @api.marshal_with(_item_list)
    @api.response(404, 'Item not found')
    @api.doc(security='apikey')
    @jwt_required()
    def get(self, item_id):
        """get item by name"""
        item = session.query(ItemModel).filter(ItemModel.id==item_id).first()
        if item:
            return item
        api.abort(404, 'Item not found')
        return

    @api.doc(security='apikey')
    @jwt_required()
    def delete(self, item_id):
        """delete item"""
        item = session.query(ItemModel).filter(ItemModel.id==item_id).first()
        if item:
            session.delete(item)
            session.commit()
        return {'message': 'Item deleted'}

    @api.marshal_with(_item_list)
    def put(self, item_id):
        """update item"""
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')
        item_to_update=session.query(ItemModel).get(item_id)
        item_to_update.name = name
        item_to_update.price = price
        session.commit()
        return item_to_update


@api.route('/item')
class ItemList(Resource):
    @api.doc(security='apikey')
    @jwt_required(optional=True)
    @api.marshal_list_with(_item_list)
    def get(self):
        """list all item"""
        all_items = session.query(ItemModel).all()
        if not all_items:
            api.abort(404)
            return
        return all_items, 200

    @jwt_required()
    @api.expect(_item_create)
    def post(self):
        """create a item"""
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')
        store_id = data.get('store_id')
        if session.query(ItemModel).filter(ItemModel.name==name,ItemModel.store_id==store_id).first():
            return {'message': "An item with name '{}' already exists.".format(name)}, 400
        item = ItemModel(name,price,store_id)
        try:
            session.add(item)
            session.commit()
        except:
            return {"message": "An error occurred inserting the item."}, 500
        return marshal(item, _item_list), 201


@api.route('/order')
class Order(Resource):
    @api.marshal_list_with(_order_list)
    def get(self):
        """list all orders"""
        all_orders = session.query(OrderModel.id,ItemModel.name,ItemModel.price).filter(OrderModel.item_id==ItemModel.id).all()
        if not all_orders:
            api.abort(404)
            return
        return all_orders, 200

    @api.expect(_order_create)
    def post(self):
        """place a order"""
        data = request.get_json()
        user_id = data.get('user_id')
        item_id = data.get('item_id')
        store_id = data.get('store_id')
        order_date=datetime.datetime.now()
        order = OrderModel(user_id,item_id,store_id,order_date)
        try:
            session.add(order)
            session.commit()
        except:
            return {"message": "An error occurred while placing an order."}, 500
        return marshal(order, _order_list), 201


@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    return {
        'is_admin': True if identity == 1 else False
    }


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload['jti'] in BLACKLIST


@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'message': 'The token has expired',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'message': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'description': 'Request does not contain an access token.',
        'error': 'authorization_required'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        'description': 'The token is not fresh.',
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'description': 'The token has been revoked.',
        'error': 'token_revoked'
    }), 401


if __name__ == "__main__":
    app.run(debug=True)