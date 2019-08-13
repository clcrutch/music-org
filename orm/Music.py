from orm.Base import Base

from sqlalchemy import Column, Integer, String

class Music(Base):
    __tablename__ = "Music"

    ID = Column(Integer, primary_key=True)