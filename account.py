from datetime import date
import datetime
import uuid
from flask_restx import Api, Resource,fields
from flask import Flask, request, session  
from base import Base,engine,Session
from accountdb import Account,Customer,Transaction

app=Flask(__name__)

api=Api(app,doc='/',title="A BANK API",description="A REST API for Banks")
app.secret_key = "a1b2c"

Base.metadata.create_all(engine)
session=Session()  

customer_model=api.model(
    'Customer',
    {
        'cus_id':fields.String(),
        'password':fields.String(),
        'cname':fields.String(),
    }
)
account_model=api.model(
    'Account',
    {
        'acc_no':fields.String(),
        'acc_type':fields.String(),
        'balance':fields.Integer(),
        'cus_id':fields.String(),
    }
)
transaction_model=api.model(
    'Transaction',
    {
        'trans_id':fields.String(),
        'acc_no':fields.String(),
        'trans_type':fields.String(),
        'trans_amount':fields.Integer(),
        'trans_date':fields.DateTime(),
    }
)


@api.route('/login')
class Login(Resource):
    @api.marshal_with(customer_model,code=200,envelope="customer")
    @api.expect(customer_model)
    def post(self):
        ''' Login '''
        data=request.get_json()
        cus_id=data.get('cus_id')
        password=data.get('password')
        check_pass=session.query(Customer).get(cus_id)
        if check_pass==password:
            account=session.query(Account).get(cus_id)
            return account,200
        else:
            return 404
   

@api.route('/register')
class Register(Resource):
    @api.marshal_with(customer_model,code=200,envelope="customer")
    @api.expect(customer_model)
    def post(self):
        ''' Register Customer'''
        data=request.get_json()
        cus_id=data.get('cus_id')
        password=data.get('password')
        cname=data.get('cname')
        reg=Customer(cus_id,password,cname)
        session.add(reg)
        session.commit()
        return reg

@api.route('/account')
class Accounts(Resource):
    @api.marshal_with(account_model,code=200,envelope="customer")
    @api.expect(account_model)
    def post(self):
        ''' Add Account '''
        data=request.get_json()
        acc_no=data.get('acc_no')
        acc_type=data.get('acc_type')
        balance=data.get('balance')
        cus_id=data.get('cus_id')
        acc=Account(acc_no,acc_type,balance,cus_id)
        session.add(acc)
        session.commit()
        return acc

@api.route('/account/<string:id>')
class Account_view(Resource):
    @api.marshal_list_with(account_model,code=200,envelope="account")
    def get(self,id):
        ''' Account Details '''
        acc=session.query(Account).get(id)
        return acc


@api.route('/transaction/<string:id>')
class Trans(Resource):
    def trans_amt(self,aid,amt):
        acc=session.query(Account).get(aid)
        acc.balance=acc[2]+amt
        session.commit()
        return acc


    @api.marshal_with(transaction_model,code=200)
    @api.expect(transaction_model)
    def post(self,id):
        ''' Transaction '''
        acc_no=id
        trans_date=datetime.datetime.now()
        trans_id=uuid.uuid4().hex[:10]
        data=request.get_json()
        trans_type=data.get('trans_type')
        trans_amount=data.get('trans_amount')
        trans=Transaction(trans_id,acc_no,trans_type,trans_amount,trans_date)
        session.add(trans)
        session.commit()
        return trans


@api.route('/statement/<string:id>')
class Statement(Resource):
    @api.marshal_list_with(transaction_model,code=200,envelope="statement")
    def get(self,id):
        ''' Account Statement '''
        statement=session.query(Transaction).filter(Transaction.acc_no==id).all()
        return statement


            
if __name__=='__main__':
    app.run(debug='True')

