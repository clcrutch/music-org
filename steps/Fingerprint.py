import acoustid
import os
import pymssql

from os import path
from sqlalchemy.orm import sessionmaker, Session

class FingerprintStep:
    priority = 10
    step_name = 'Fingerprint'

    def execute(self, file_name: str, db_session: sessionmaker, conn: pymssql.Connection) -> (str, bool):
        # List of possible audio formats.
        audio_formats = [
            'mp3',
            'm4a'
        ]

        # Get the extension.
        name, ext = path.splitext(file_name)
        ext = ext[1:].lower()

        # If it's not music or is an empty file, move it
        if not ext in audio_formats or path.getsize(file_name) == 0:
            name = path.basename(file_name)
            new_name = path.join('./shares/not-music/', name)
            os.rename(file_name, new_name)

            return new_name, False

        print(file_name)
        # Compute the fingerprint
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
        # Determine where we should move the file.
        name = path.basename(file_name)
        duplicate_name = './shares/duplicate-music/' + name

        # Move the file.
        os.rename(file_name, duplicate_name)

        return duplicate_name
