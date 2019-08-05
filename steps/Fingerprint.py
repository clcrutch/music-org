import acoustid
import pymssql

from os import rename
from os.path import basename, getsize, join, splitext

class FingerprintStep:
    priority = 10
    step_name = 'Fingerprint'

    def execute(self, file_name: str, conn: pymssql.Connection) -> (str, bool):
        audio_formats = [
            'mp3',
            'm4a'
        ]

        name, ext = splitext(file_name)
        ext = ext[1:].lower()

        if not ext in audio_formats or getsize(file_name) == 0:
            name = basename(file_name)
            new_name = join('./shares/not-music/', name)
            rename(file_name, new_name)

            return new_name, False

        print(file_name)
        length, fingerprint = acoustid.fingerprint_file(file_name)

        if not self.music_file_exists(fingerprint, conn):
            # If this is not a duplicate, then we add it to the list
            cursor: pymssql.Cursor = conn.cursor()
            cursor.execute(
                'DECLARE @Fingerprint VARBINARY(MAX) = CAST(%s AS VARBINARY(MAX));' +
                'EXEC sp_InsertFile %s, %d, @Fingerprint',
                (fingerprint, file_name, length)
            )
            cursor.close()

            return (file_name, True)
        else:
            # Move the file so that a human can review.
            return (self.handle_duplicate_files(file_name), False)

    def music_file_exists(self, fingerprint: str, conn: pymssql.Connection) -> bool:
        cursor: pymssql.Cursor = conn.cursor()

        # Get the fingerprint count to check if it's already there.
        cursor.execute('SELECT COUNT(*) FROM Music WHERE Fingerprint = %s', fingerprint)
        fingerprint_count = cursor.fetchone()[0]

        cursor.close()

        return fingerprint_count > 0

    def handle_duplicate_files(self, file_name: str) -> str:
        name = basename(file_name)
        duplicate_name = './shares/duplicate-music/' + name

        # Move the file.
        rename(file_name, duplicate_name)

        return duplicate_name
