from sqlalchemy import Integer, String,Column
from base import Base

  
class Employees(Base):  
    __tablename__='employees'

    id = Column(Integer, primary_key = True)  
    name = Column(String)  
    salary = Column(Integer)  
    age = Column(Integer)   
    pin = Column(String)  
  
    def __init__(self, name, salary, age,pin):  
      self.name = name  
      self.salary = salary  
      self.age = age  
      self.pin = pin  
 
