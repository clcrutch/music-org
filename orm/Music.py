from orm.Base import Base

from sqlalchemy import Column, Integer, NVARCHAR, FLOAT, VARBINARY

class Music(Base):
    __tablename__ = 'Music'

    id = Column(Integer, primary_key=True, name='ID')
    file_path = Column(NVARCHAR, name='FilePath')
    length = Column(FLOAT, name='Length')
    fingerprint = Column(VARBINARY, name='Fingerprint')
    music_brainz_id = Column(NVARCHAR(256), name='MusicBrainzID')
    title = Column(NVARCHAR(256), name='Title')
    album_id = Column(Integer, name='AlbumID')
    track = Column(Integer, name='Track')
    genre = Column(NVARCHAR(256), name='Genre')
    lyrics = Column(NVARCHAR, name='Lyrics')