from sqlalchemy.ext.declarative import declarative_base
from .BaseEmpty import BaseEmpty

BoxBase = declarative_base()
MetaDataBase = declarative_base()
TaskBase = declarative_base()

def to_dict(self):
    return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}

BoxBase.to_dict = to_dict
MetaDataBase.to_dict = to_dict
TaskBase.to_dict = to_dict


