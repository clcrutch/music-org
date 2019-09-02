from orm.Base import Base

from sqlalchemy import Column, Integer, NVARCHAR

class Step(Base):
    __tablename__ = 'Steps'

    id = Column(Integer, primary_key=True, name='ID')
    music_id = Column(Integer, name='MusicID')
    step_name = Column(NVARCHAR(64), name='StepName')