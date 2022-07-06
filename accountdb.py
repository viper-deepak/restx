from sqlalchemy import DateTime, ForeignKey, column, create_engine,Integer,Column,String
from base import Base


    

class Customer(Base):
    __tablename__='customer'
    cus_id=Column(String(10),primary_key=True)
    password=Column(String)
    cname=Column(String)

    def __init__(self,cus_id,password,cname):  
        self.cus_id = cus_id  
        self.password = password
        self.cname=cname

class Account(Base):
    __tablename__='account'
    acc_no=Column(String(10),primary_key=True)
    acc_type=Column(String)
    balance=Column(Integer)
    cus_id=Column(String(10),ForeignKey('customer.cus_id'))

    def __init__(self,acc_no,acc_type,balance,cus_id):  
        self.acc_no = acc_no  
        self.acc_type = acc_type
        self.balance=balance
        self.cus_id=cus_id

class Transaction(Base):
    __tablename__='trans'
    trans_id=Column(String(10),primary_key=True)
    acc_no=Column(String(10),ForeignKey('account.acc_no'))
    trans_type=Column(String)
    trans_amount=Column(Integer)
    trans_date=Column(DateTime)

    def __init__(self,trans_id,acc_no,trans_type,trans_amount,trans_date):  
        self.trans_id = trans_id
        self.acc_no = acc_no   
        self.trans_type = trans_type
        self.trans_amount=trans_amount
        self.trans_date=trans_date