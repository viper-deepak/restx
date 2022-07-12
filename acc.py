from flask import Flask, jsonify,request
import pypyodbc
from flask_restx import Api, Resource,fields
from datetime import date
import datetime
import uuid

app=Flask(__name__)
api=Api(app,doc='/',title="A Bank API",description="A REST API for Bank Account")

app.secret_key = "a1b2c"
conn='Driver={SQL Server};Server=.;Database=sample;uid=sa;pwd=Admin@12345'


customer_model=api.model(
    'Customer',
    {
        'cid':fields.String(),
        'cname':fields.String(),
    }
)
account_model=api.model(
    'Account',
    {
        'ano':fields.String(),
        'atype':fields.String(),
        'balance':fields.Integer(),
        'cid':fields.String(),
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
class CustomerLogin(Resource):
    @api.expect(customer_model)
    def post():
        if request.method=="POST":
            data=request.get_json()
            cid=data.get('cid')
            with pypyodbc.connect(conn) as con: 
                cur=con.cursor()
                cur.execute("select cname from customers where cid='%s'"%cid )
                customer_name=cur.fetchone()
                if customer_name:
                    return jsonify({
                        'cname':customer_name
                    })
                else:
                    error="invalid customer id"
                    return error

@api.route('/home/<string:id>')
class Home(Resource):
    def get(id):
            data=request.get_json()
            cid=data.get('cid')
            with pypyodbc.connect(conn) as con: 
                cur=con.cursor()
                cur.execute("select cname,ano,atype,balance from customers as c, account as a where c.cid=a.cid and c.cid='%s' group by cname,ano,atype,balance"%cid )
                rows=cur.fetchall()
            return jsonify({
                'cname':rows[0],
                'ano':rows[1],
                'atype':rows[2],
                'balance':rows[3]
            })
    

    
            
if __name__=='__main__':
    app.run(debug='True')

