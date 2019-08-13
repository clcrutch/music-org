from orm.Base import Base

from sqlalchemy import Column, Integer, NVARCHAR

class Music(Base):
    __tablename__ = "Music"

    id = Column(Integer, primary_key=True, name='ID')
    file_path = Column(NVARCHAR, name='FilePath')