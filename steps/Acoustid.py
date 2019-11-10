import acoustid
import os
import pymssql

from sqlalchemy.orm import sessionmaker, Session

class AcoustidStep:
    priority = 30
    step_name = 'Acoustid'

    def execute(self, file_name: str, db_session: sessionmaker, conn: pymssql.Connection) -> (str, bool):
        # Get the secrets from environment.
        api_key = os.environ['ACOUSTID_API_KEY']

        cursor: pymssql.Cursor = conn.cursor()

        # Fetch the fingerprint and length
        cursor.execute('EXEC sp_SelectFileFingerprintLength %s', file_name)
        length, fingerprint = cursor.fetchone()

        # Get the results from acoustid.
        results = acoustid.parse_lookup_result(acoustid.lookup(api_key, fingerprint, length))
        results = [r for r in results if r[3] is not None]

        # If we don't want have any results from the fingerprint, that's fine.
        if len(results) == 0:
            return file_name, True

        # We want to select the most confident answer.
        max_confidence = max([r[0] for r in results])

        results = [r for r in results if r[0] == max_confidence]

        # Store all possible results.
        for song in results:
            cursor.execute(
                'EXEC sp_InsertPossibleMatches %s, %s, %s, %s', (file_name, song[3], song[2], song[1])
            )

        cursor.close()
        return (file_name, True)
