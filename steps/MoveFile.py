import pymssql

from os import mkdir, rename
from os.path import isdir, join

class MoveFileStep:
    priority = 70
    step_name = 'MoveFile'

    def execute(self, file_name: str, conn: pymssql.Connection) -> (str, bool):
        base_folder = './shares/music'

        cursor: pymssql.Cursor = conn.cursor()
        cursor.execute('EXEC sp_SelectSongLocationInfo %s', file_name)
        artist, album, track_number, title = cursor.fetchone()

        artist = artist.replace('/', '_')
        album = album.replace('/', '')
        title = title.replace('/', '')

        folder = join(base_folder, artist + ' - ' + album)
        new_file_name = str(track_number) + ' - ' + title

        if not isdir(folder):
            mkdir(folder)

        base_path = join(folder, new_file_name)
        new_file_path = base_path + '.mp3'
        lyrics_path = base_path + '.txt'

        cursor.execute('EXEC sp_SelectLyrics %s', file_name)
        lyrics = cursor.fetchone()[0]

        if lyrics is not None:
            with open(lyrics_path, 'w')  as f:
                f.write(lyrics)

        rename(file_name, new_file_path)

        cursor.execute('EXEC sp_UpdatePath %s, %s', (file_name, new_file_path))

        cursor.close()

        return new_file_path, True
