from Base import Base

from sqlalchemy import Column, Integer, String

class Music(Base):
    __table_name__ = "Music"

    ID = Column(Integer, primary_key=True)