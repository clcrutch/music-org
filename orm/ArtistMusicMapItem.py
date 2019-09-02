from orm.Base import Base

from sqlalchemy import Column, Integer

class ArtistMusicMapItem(Base):
    __tablename__ = 'ArtistMusicMap'

    id = Column(Integer, primary_key=True, name='ID')
    music_id = Column(Integer, name='MusicID')
    artist_id = Column(Integer, name='ArtistID')