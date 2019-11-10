import itertools
import musicbrainzngs
import pymssql

from sqlalchemy.orm import sessionmaker, Session

class MusicBrainzStep:
    priority = 40
    step_name = 'MusicBrainz'

    def execute(self, file_name: str, db_session: sessionmaker, conn: pymssql.Connection) -> (str, bool):
        musicbrainzngs.set_useragent('music-org', '0.1')

        cursor: pymssql.Cursor = conn.cursor()

        # Get all possible matches returned from Acoustid
        cursor.execute(
            'EXEC sp_SelectPossibleMatches %s', file_name
        )

        # If there are no matches, then just continue.
        if cursor.rowcount == 0:
            return file_name, True

        # Get all rows.
        rows = list(cursor.fetchall())

        # We want the MusicBrainz ID from the possible matches.
        musicBrainzIDs = [r[2] for r in rows]

        # Get releases from MusicBrainz
        releases = []
        for row in rows:
            result: dict = musicbrainzngs.search_recordings(artist = row[0], recording = row[1])

            releases = releases + [r for r in result['recording-list'] if r['id'] in musicBrainzIDs]

        release_group = self.get_release_group(releases)
        # If we can't find any albums, return.
        if release_group is None:
            return file_name, True
        
        # Get the recording in the albums
        recordings = [r for r in musicbrainzngs.search_recordings(release = release_group['title'])['recording-list'] if r['id'] in musicBrainzIDs]            

        if len(recordings) != 0:
            recording = recordings[0]
        else:
            # Could not find on MusicBrainz
            return file_name, True

        artists = [(r['artist']['id'], r['artist']['name'], file_name) for r in recording['artist-credit']]
        cursor.executemany(
            'EXEC sp_InsertIntoArtists %s, %s, %s',
            artists
        )

        release_group_countries = [r for r in recording['release-list'] if r['release-group']['id'] == release_group['id']]
        release_group_country = [r for r in release_group_countries if r['country'] == 'US'][0]

        # Genre
        tags = recording['tag-list']
        tags.sort(key = lambda x: x['name'])
        tag = tags[0]['name']
        
        tag = tag[:1].upper() + tag[1:]

        cover_art_data = musicbrainzngs.caa.get_release_group_image_front(release_group['id'])

        cursor.execute(
            'DECLARE @Date DATE = CAST(%s AS DATE);' +
            'DECLARE @CoverArt VARBINARY(MAX) = CAST(%s AS VARBINARY(MAX));' +
            'EXEC sp_UpdateMusic %s, %s, @Date, @CoverArt, %s, %s, %s, %d, %s, %s',
            (
                release_group['first-release-date'],
                cover_art_data,
                release_group['id'],
                release_group['title'],
                'image/jpeg',
                recording['id'],
                recording['title'],
                int(release_group_country['medium-list'][0]['track-list'][0]['number']),
                tag,
                file_name
            )
        )

        cursor.close()

        return (file_name, True)

    def get_release_group(self, releases):
        release_lists = [r['release-list'] for r in releases if 'release-list' in releases]

        if len(release_lists) == 0:
            return None

        release_lists = list(itertools.chain(*release_lists))
        
        release_groups = [r['release-group'] for r in release_lists]

        # Songs have multiple albums, we want thme in this order.
        release_preferences = ['Album', 'Single', 'EAP']
        for preference in release_preferences:
            release_groups = [r for r in release_groups if r['primary-type'] == preference]

            if len(release_groups) > 0:
                break

        # Get the albums
        release_groups = [musicbrainzngs.get_release_group_by_id(r['id'])['release-group'] for r in release_groups]

        dates = [r['first-release-date'] for r in release_groups]
        dates = [d for d in dates if d.count('-') > 0]

        # We want the earlies album.
        initial_date = min(dates)

        # Get the earliest album.
        release_groups = [r for r in release_groups if r['first-release-date'] == initial_date]
        return release_groups[0]
 
