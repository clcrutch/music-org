from orm.Base import Base

from sqlalchemy import Column, Integer, NVARCHAR

class OriginalFile(Base):
    __tablename__ = 'OriginalFiles'

    id = Column(Integer, primary_key=True, name='ID')
    music_id = Column(Integer, name='MusicID')
    original_file_path = Column(NVARCHAR, name='OriginalFilePath')