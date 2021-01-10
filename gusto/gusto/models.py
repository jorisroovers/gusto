from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,Unicode

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(Unicode)

    def __repr__(self):
       return "<Account(name='%s', description='%s')>" % (self.name, self.description)