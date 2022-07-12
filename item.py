from flask import request,session
from flask_restx import Resource,fields,Namespace
from model import ItemModel
from flask_restx.marshalling import marshal


api = Namespace("items",description="items related operations")



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



@api.route('/item')
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
        if session.query(ItemModel).filter(ItemModel.name==name,ItemModel.store_id==store_id).first():
            return {'message': "An item with name '{}' already exists.".format(name)}, 400
        item = ItemModel(name,price,store_id)
        try:
            session.add(item)
            session.commit()
        except:
            return {"message": "An error occurred inserting the item."}, 500
        return marshal(item, _item_list), 201


