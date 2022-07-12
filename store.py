from flask import request,session
from flask_restx import Resource,fields,Namespace
from model import StoreModel
from flask_restx.marshalling import marshal


api = Namespace("store",description="store related operations")

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


@api.route('/store')
class StoreList(Resource):
    @api.marshal_list_with(_store_list)
    def get(self):
        """list all stores"""
        store=session.query(StoreModel).order_by(StoreModel.id).all()
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



@api.route('/store/<name>')
class Store(Resource):
    @api.response(404, 'Store not found.')
    @api.marshal_with(_store_list)
    def get(self, name):
        """get a store"""
        store = session.query(StoreModel).filter(StoreModel.name==name).first().items.all()
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
