from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from empty import BoxBase


class Box(BoxBase):
    __tablename__ = 'box_info'
    box_id: str = Column(String(36), primary_key=True)
    box_path: str = Column(String(128))
    box_name: str = Column(String(128), default="新建分区")
    box_mark: str = Column(String(1000))
    enable: bool = Column(Boolean())
    v_del: bool = Column(Boolean())
    # keys =relationship("BoxKey",back_populates = "box_obj")

# 6137d0e0-bc4c-4f77-99eb-8a5a2e007bdf,D:\fos\经侦通知通报,经侦通知通报,"",1

class BoxKey(BoxBase):
    __tablename__ = 'key_info'
    key_id: str = Column(String(36), primary_key=True)
    box_id: str = Column(String(36), ForeignKey("box_info.box_id",ondelete='RESTRICT'))
    # box_obj =relationship("Box",back_populates = "keys")
    # box_id: str = Column(String(36), ForeignKey("box_info.box_id"))
    read_perm: bool = Column(Boolean())
    write_perm: bool = Column(Boolean())
