from database import Base
from sqlalchemy import String, Boolean, Integer, Column

class User(Base):
    __tablename__ = "Users"
    
    #id=Column(Integer, primary_key=True, index=True)
    username=Column(String, primary_key=True, index=True)
    email=Column(String, unique=True, index=True)
    password=Column(String)
    