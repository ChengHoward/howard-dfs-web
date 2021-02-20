from sqlalchemy import Column, String, Boolean, Integer
from empty import TaskBase


class Task(TaskBase):
    __tablename__ = 'task_info'
    task_id: str = Column(String(36), primary_key=True)
    enable: bool = Column(Boolean())
    content: str = Column(String(36))
    time: str = Column(String(36))
    label: str = Column(String(36))
    command: str = Column(String(512))
    mark: str = Column(String(512))