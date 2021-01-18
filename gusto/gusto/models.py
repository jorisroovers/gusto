from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,Unicode

Base = declarative_base()

class Recipe(Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    description = Column(Unicode)
    comments = Column(Unicode)
    url = Column(Unicode)
    tags = Column(Unicode)

    def __repr__(self):
       return f"<Recipe(name='{self.name}')>"