from sqlalchemy import Column, String, Boolean, Integer
from empty import MetaDataBase


def create_MetaData(tablename):
    class MetaData(MetaDataBase):
        # __tablename__ = 'mate_data_info'
        __tablename__ = tablename
        file_id: str = Column(String(36), primary_key=True)
        file_path: str = Column(String(36), nullable=True)
        file_name: str = Column(String(128), nullable=True)
        file_old_name: str = Column(String(128), nullable=True)
        file_suffix: str = Column(String(16), nullable=True)
        file_size: int = Column(Integer(), default=0)
        label: str = Column(String(128), default="default")
        rel: str = Column(String(36), unique=True)
        v_del: bool = Column(Boolean())

    return MetaData