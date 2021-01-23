from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Unicode, Date, ForeignKey

import sqlalchemy.types as types

from .constraints import CONSTRAINTS

Base = declarative_base()


class GustoModel:

   def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class CSVList(types.TypeDecorator):
   """ Custom type for DB colums to store/retrieve python lists as CSV strings """
   impl = Unicode

   def process_literal_param(self, value, dialect):
       if value:
         return ",".join(value)

   def process_result_value(self, value, dialect):
      if value:
         return value.split(",")

class Recipe(Base, GustoModel):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    description = Column(Unicode)
    comments = Column(Unicode)
    url = Column(Unicode)
    tags = Column(CSVList)

    def __repr__(self):
       return f"<Recipe(name='{self.name}')>"

class Meal(Base, GustoModel):
   __tablename__ = 'meals'

   id = Column(Integer, primary_key=True)
   date = Column(Date)
   recipe_id = Column(Integer, ForeignKey('recipes.id'))
   recipe = relationship("Recipe")
   constraint_name = Column(Unicode)

   @property
   def constraint(self):
      return CONSTRAINTS.get(self.constraint_name, None)

   def __repr__(self):
      return f"<Meal(date='{self.date}' recipe='{self.recipe.name}')>"
   
   def as_dict(self):
      return {'id': self.id, 'date': self.date.strftime("%Y-%m-%d"), 
            'recipe': self.recipe.as_dict(),
            'constraint' : self.constraint
            }