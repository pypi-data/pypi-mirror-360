from sqlalchemy import create_engine, MetaData

DATABASE_URL = "mysql://user:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
metadata = MetaData()