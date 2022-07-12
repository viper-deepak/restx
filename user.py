from flask import request,session
from flask_restx import Resource,fields,Namespace
from model import UserModel


api = Namespace("users",description="users related operations")


_user_list = api.model('_user_list', {
    'id': fields.Integer(readonly=True, description="The user identifier"),
    'username': fields.String(required=True, description="The user name"),
})
_user_create = api.model('_user_create', {
    'username': fields.String(required=True, description="The username"),
    'password': fields.String(required=True, description="The user password"),
})




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


