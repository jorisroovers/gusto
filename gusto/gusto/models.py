from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Unicode, Date, ForeignKey

Base = declarative_base()

class Recipe(Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, unique=True)
    description = Column(Unicode)
    comments = Column(Unicode)
    url = Column(Unicode)
    tags = Column(Unicode)

    def __repr__(self):
       return f"<Recipe(name='{self.name}')>"

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
class Meal(Base):
    __tablename__ = 'meals'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    recipe_id = Column(Integer, ForeignKey('recipes.id'))
    recipe = relationship("Recipe")

    def __repr__(self):
       return f"<Meal(date='{self.date}' recipe='{self.recipe.name}')>"