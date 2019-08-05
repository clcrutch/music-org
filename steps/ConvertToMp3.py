import ffmpeg
import pymssql
import time

from os import remove, rename
from os.path import abspath, basename, exists, join, splitext
from shutil import copyfile

class ConvertToMp3Step:
    priority = 20
    step_name = 'ConvertToMp3'

    def handle_duplicate_files(self, file_name: str) -> str:
        name = basename(file_name)
        duplicate_name = './shares/duplicate-music/' + name

        # Move the file.
        rename(file_name, duplicate_name)

        return duplicate_name

    def execute(self, file_name: str, conn: pymssql.Connection) -> (str, bool):
        name, ext = splitext(file_name)
        ext = ext[1:].lower()

        if ext != 'mp3':
            new_file_name = name + '.mp3'
            tmp_name = timestr = time.strftime("%Y%m%d-%H%M%S") + '.mp3'

            (
                ffmpeg
                .input(file_name)
                .output(tmp_name, map_metadata='0')
                .run()
            )

            copyfile(tmp_name, new_file_name)
            remove(tmp_name)

            cursor: pymssql.Cursor = conn.cursor()
            cursor.execute('EXEC sp_UpdatePath %s, %s', (file_name, new_file_name))
            cursor.close()

            self.handle_duplicate_files(file_name)

            return new_file_name, True
            

        return file_name, True
