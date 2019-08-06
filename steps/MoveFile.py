import os
import pymssql

from os import path

class MoveFileStep:
    priority = 70
    step_name = 'MoveFile'

    def execute(self, file_name: str, conn: pymssql.Connection) -> (str, bool):
        # Get the folder we are moving the music to.
        base_folder = './shares/music'

        # Get the info to compute the new location for the song.
        cursor: pymssql.Cursor = conn.cursor()
        cursor.execute('EXEC sp_SelectSongLocationInfo %s', file_name)
        artist, album, track_number, title = cursor.fetchone()

        # Update the values to be path safe.
        artist = artist.replace('/', '_')
        album = album.replace('/', '')
        title = title.replace('/', '')

        # Get the filder name.
        folder = path.join(base_folder, artist + ' - ' + album)
        # Get the file name.
        new_file_name = str(track_number) + ' - ' + title

        # Create the path if it does nto exist.
        if not path.isdir(folder):
            os.mkdir(folder)

        # Get the path without the extension.
        base_path = path.join(folder, new_file_name)
        new_file_path = base_path + '.mp3'
        lyrics_path = base_path + '.txt'

        # Get the lyrics
        cursor.execute('EXEC sp_SelectLyrics %s', file_name)
        lyrics = cursor.fetchone()[0]

        # If we have lyrics, save them.
        if lyrics is not None:
            with open(lyrics_path, 'w')  as f:
                f.write(lyrics)

        # Move the music file.
        os.rename(file_name, new_file_path)

        # Update new information.
        cursor.execute('EXEC sp_UpdatePath %s, %s', (file_name, new_file_path))

        cursor.close()

        return new_file_path, True
