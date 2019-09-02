from orm.Base import Base

from sqlalchemy import Column, Integer, NVARCHAR, VARBINARY, DATE

class Album(Base):
    __tablename__ = 'Albums'

    id = Column(Integer, primary_key=True, name='ID')
    music_brainz_id = Column(NVARCHAR(256), name='MusicBrainzID')
    name = Column(NVARCHAR(256), name='Name')
    date = Column(DATE, name='Date')
    cover_art = Column(VARBINARY, name='CoverArt')
    mime_type = Column(NVARCHAR(64), name='MimeType')