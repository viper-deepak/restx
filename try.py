from flask import Flask,request
from flask_restx import Api, Resource,fields
from book import Books
from base import Base,engine,Session
from sqlalchemy import create_engine,Integer, String,Column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base


app=Flask(__name__)

api=Api(app,doc='/',title="A book API",description="A REST API for books")

conn='Driver={SQL Server};Server=.;Database=sample;uid=sa;pwd=Admin@12345'
connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": conn})
engine = create_engine(connection_url)  
Session=sessionmaker(bind=engine)
Base=declarative_base()

  
class Books(Base):  
    __tablename__='books'

    id = Column(Integer, primary_key = True)  
    title = Column(String)  
    author = Column(String)  

  
    def __init__(self,title,author):  
      self.title = title  
      self.author = author  

book_model=api.model(
    'Book',
    {
        'id':fields.Integer(),
        'title':fields.String(),
        'author':fields.String(),
    }
)

Base.metadata.create_all(engine)
session=Session()  

@api.route('/books')
class Book(Resource):

    @api.marshal_list_with(book_model,code=200,envelope="books")
    def get(self):
        ''' Get all Books '''
        books=session.query(Books).all()
        return books

    @api.marshal_with(book_model,code=201,envelope="book")
    @api.expect(book_model)
    def post(self):
        ''' Create a new book '''
        data=request.get_json()
        title=data.get('title')
        author=data.get('author')
        new_book=Books(title,author)
        session.add(new_book)
        session.commit()
        return new_book


@api.route('/book/<int:id>')
class BookResource(Resource):

    @api.marshal_with(book_model,code=200,envelope="book")
    def get(self,id):
        ''' Get a book by id '''
        book=session.query(Books).get(id)
        return book,200

    @api.marshal_with(book_model,envelope="book",code=200)
    @api.expect(book_model)
    def put(self,id):
        ''' Update a book '''
        book_to_update=session.query(Books).get(id)
        data=request.get_json()
        book_to_update.title=data.get('title')
        book_to_update.author=data.get('author')
        session.commit()
        return book_to_update,200

    @api.marshal_with(book_model,envelope="book_deleted",code=200)
    def delete(self,id):
        '''Delete a book'''
        book_to_delete=session.query(Books).filter(Books.id==id).first()
        session.delete(book_to_delete)
        session.commit()
        return book_to_delete,200

if __name__ == "__main__":
    app.run(debug=True)