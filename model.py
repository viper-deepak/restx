from xmlrpc.client import DateTime
from sqlalchemy import Integer, String,Column,Float,ForeignKey,Table,DateTime
from sqlalchemy.orm import relationship
from base import Base



class StoreModel(Base):
    __tablename__ = 'stores'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80))

    items = relationship("ItemModel", order_by = 'ItemModel.id', back_populates = "store")

    def __init__(self, name):
        self.name = name


class ItemModel(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80))
    price = Column(Float(precision=2))

    store_id = Column(Integer, ForeignKey('stores.id'))
    store = relationship('StoreModel',back_populates="items")

    def __init__(self, name, price, store_id):
        self.name = name
        self.price = price
        self.store_id = store_id


class UserModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80))
    password = Column(String(80))

    orders = relationship("OrderModel", order_by = 'OrderModel.id', back_populates = "user")

    def __init__(self, username, password):
        self.username = username
        self.password = password


class OrderModel(Base):
    __tablename__ = 'orders'

    id = Column(Integer,primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    store_id = Column(Integer, ForeignKey('stores.id'))
    order_date =  Column(DateTime)

    user = relationship('UserModel',back_populates="orders")

    def __init__(self,user_id,item_id,store_id,order_date):
        self.user_id = user_id
        self.item_id = item_id
        self.store_id = store_id
        self.order_date = order_date
