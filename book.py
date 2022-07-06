from sqlalchemy import Integer, String,Column
from base import Base

  
class Books(Base):  
    __tablename__='books'

    id = Column(Integer, primary_key = True)  
    title = Column(String)  
    author = Column(String)  

  
    def __init__(self,title,author):  
      self.title = title  
      self.author = author  
 
