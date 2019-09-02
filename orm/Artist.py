from orm.Base import Base

from sqlalchemy import Column, Integer, NVARCHAR, DATE

class Artist(Base):
    __tablename__ = 'Artists'

    id = Column(Integer, primary_key=True, name='ID')
    music_brainz_id = Column(NVARCHAR(256), name='MusicBrainzID')
    name = Column(NVARCHAR(256), name='Name')