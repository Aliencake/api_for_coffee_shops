from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:root@localhost:3306/api_for_coffee_shops_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()
