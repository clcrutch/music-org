import eyed3
import pymssql

class UpdateTagsStep:
    priority = 50
    step_name = 'UpdateTags'

    def execute(self, file_name: str, conn: pymssql.Connection) -> (str, bool):
        eyed3.log.setLevel("ERROR")

        audiofile = eyed3.load(file_name)

        tag_artist = audiofile.tag.artist or audiofile.tag.album_artist
        tag_album = audiofile.tag.album
        tag_album_date = audiofile.tag.best_release_date

        if tag_album_date is not None:
            tag_album_date = str(tag_album_date)

        tag_genre = audiofile.tag.genre

        if tag_genre is not None:
            tag_genre = tag_genre.name

        tag_track_number = audiofile.tag.track_num[0]
        tag_title = audiofile.tag.title
        tag_image = audiofile.tag.images.get('')

        tag_cover_art = None
        tag_mime_type = None

        if tag_image is not None:
            tag_cover_art = tag_image.image_data
            tag_mime_type = tag_image.mime_type

        cursor: pymssql.Cursor = conn.cursor()
        cursor.execute(
            'EXEC sp_SelectSongTags %s',
            file_name
        )
        row = cursor.fetchone()

        if row is None:
            row = (None, None, None, None, None, None, None, None)

        sql_artist, sql_album, sql_album_date, sql_cover_art, sql_mime_type, sql_genre, sql_track_number, sql_title = row

        artist = sql_artist or tag_artist
        album = sql_album or tag_album
        album_date = sql_album_date or tag_album_date
        genre = sql_genre or tag_genre
        track_number = sql_track_number or tag_track_number
        title = sql_title or tag_title
        cover_art = sql_cover_art or tag_cover_art
        mime_type = sql_mime_type or tag_mime_type

        cursor.execute(
            'DECLARE @CoverArt VARBINARY(MAX) = CAST(%s AS VARBINARY(MAX));' +
            'EXEC sp_UpdateSongTags %s, %s, %s, @CoverArt, %s, %s, %d, %s, %s',
            (cover_art, artist, album, album_date, mime_type, genre, track_number, title, file_name)
        )

        audiofile.tag.artist = artist
        audiofile.tag.album = album
        audiofile.tag.genre = genre
        audiofile.tag.track_num = track_number
        audiofile.tag.title = title

        if cover_art is not None and mime_type is not None:
            audiofile.tag.images.remove('')
            audiofile.tag.images.set(3, cover_art, mime_type, '')

        try:
            audiofile.tag.save()
        except:
            pass

        cursor.close()

        return file_name, True
