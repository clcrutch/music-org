from orm.Base import Base

from sqlalchemy import Column, Integer, NVARCHAR, DATE

class PossibleMatch(Base):
    __tablename__ = 'PossibleMatches'

    id = Column(Integer, primary_key=True, name='ID')
    music_id = Column(Integer, name='MusicID')
    artist = Column(NVARCHAR(256), name='Artist')
    title = Column(NVARCHAR(256), name='Title')
    music_brainz_id = Column(NVARCHAR(256), name='MusicBrainzID')