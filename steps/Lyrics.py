import lyricsgenius
import os
import pymssql

class LyricsStep:
    priority = 60
    step_name = 'Lyrics'

    def execute(self, file_name: str, conn: pymssql.Connection) -> (str, bool):
        # Get the secrets from the environment
        api_key = os.environ['LYRIC_GENIUS_API_KEY'] 
        
        genius = lyricsgenius.Genius(api_key)

        cursor: pymssql.Cursor = conn.cursor()
        cursor.execute('EXEC sp_SelectSongTitleArtist %s', file_name)
        title, artist = cursor.fetchone()

        # Get the song from the internet.
        song = genius.search_song(title, artist=artist)

        # Save the lyrics in the db.
        if song is not None:
            cursor.execute('EXEC sp_UpdateSongLyrics %s, %s', (song.lyrics, file_name))

        return file_name, True
