from database import Base
from sqlalchemy import String, Boolean, Integer, Column, ARRAY, JSON

class User(Base):
    __tablename__ = "Users"
    
    username=Column(String, primary_key=True, index=True)
    email=Column(String, unique=True, index=True)
    password=Column(String)
    

class Movies(Base):
    __tablename__ = "Movies"

    title = Column(String)
    release_date = Column(String)
    image_url = Column(String)
    genre = Column(String)
    length = Column(String)
    description = Column(String)
    actors = Column(JSON)
    director = Column(String)
    screenplay = Column(String)
    link = Column(String, unique = True)
    id = Column(String, primary_key = True)


class Games(Base):
    __tablename__ = "Games"

    title = Column(String)
    image_url = Column(String)
    description = Column(String)
    release_date = Column(String)
    developer = Column(String)
    publisher = Column(String)
    genres = Column(ARRAY(String))
    link = Column(String, primary_key = True)


class Books(Base):
    __tablename__ = "Books"

    title = Column(String)
    author = Column(String)
    image_url = Column(String)
    description = Column(String)
    publication_info = Column(String)
    genres = Column(ARRAY(String))
    pages = Column(String)
    link = Column(String, unique = True)
    id = Column(String, primary_key = True)