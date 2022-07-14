
from base import Base,engine,Session
from model import OrderModel
import datetime

Base.metadata.create_all(engine)
session=Session() 


order_time=datetime.datetime.now()
order = OrderModel(1,2,1,order_time)
session.add(order)
session.commit()