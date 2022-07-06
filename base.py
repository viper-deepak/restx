from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL

conn='Driver={SQL Server};Server=.;Database=FlaskDB;uid=sa;pwd=Admin@12345'
connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": conn})
engine = create_engine(connection_url)  
Session=sessionmaker(bind=engine)
Base=declarative_base()

