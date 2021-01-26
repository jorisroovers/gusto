from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Unicode, Date, ForeignKey

import sqlalchemy.types as types

from .constraints import CONSTRAINTS

Base = declarative_base()


def startup(db_session):
   """ Should be called on program startup """
   TagList.fetch_tags(db_session)

class GustoModel:

   @staticmethod
   def serialize_val(value):
      if type(value) == list:
         value = [GustoModel.serialize_val(i) for i in value]
      elif hasattr(value, "as_dict"):
         value = value.as_dict()
      return value

   def as_dict(self):
      return_dict = {}
      for c in self.__table__.columns:
         return_dict[c.name] = GustoModel.serialize_val(getattr(self, c.name))

      return return_dict 

class CSVList(types.TypeDecorator):
   """ Custom type for DB colums to store/retrieve python lists as CSV strings """
   impl = Unicode

   def process_literal_param(self, value, dialect):
       if value:
         return ",".join(value)

   def process_result_value(self, value, dialect):
      if value:
         return value.split(",")
      return []

class TagList(CSVList):

   @classmethod
   def fetch_tags(cls, db_session):
      cls.tags  = dict({(t.name, t) for t in db_session.query(Tag).all()})

   def process_literal_param(self, taglist, dialect):
      tag_name_list = [t.name for t in taglist]
      return super().process_literal_param(tag_name_list, dialect)

   def process_result_value(self, value, dialect):
      tag_name_list = super().process_result_value(value, dialect)
      return [self.tags[tag_name] for tag_name in tag_name_list ]

class Tag(Base, GustoModel):
   __tablename__ = 'tags'

   name = Column(Unicode, primary_key=True)
   display_name = Column(Unicode)

   def __repr__(self):
      return f"<Tag(name='{self.name}' display_name='{self.display_name}')>"

   def as_dict(self):
      return {'name': self.name, 'display_name': self.display_name}
class Recipe(Base, GustoModel):
   __tablename__ = 'recipes'

   id = Column(Integer, primary_key=True)
   name = Column(Unicode, unique=True)
   description = Column(Unicode)
   comments = Column(Unicode)
   url = Column(Unicode)
   tags = Column(TagList)

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