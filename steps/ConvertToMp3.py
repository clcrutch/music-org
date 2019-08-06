import ffmpeg
import os
import pymssql
import shutil
import time

from os import path

class ConvertToMp3Step:
    priority = 20
    step_name = 'ConvertToMp3'

    def handle_duplicate_files(self, file_name: str) -> str:
        # Figure out where we should move the file.
        name = path.basename(file_name)
        duplicate_name = './shares/duplicate-music/' + name

        # Move the file.
        os.rename(file_name, duplicate_name)

        return duplicate_name

    def execute(self, file_name: str, conn: pymssql.Connection) -> (str, bool):
        # Get the extension for the file
        name, ext = path.splitext(file_name)
        ext = ext[1:].lower()

        # Convert the file to mp3 if not.
        if ext != 'mp3':
            new_file_name = name + '.mp3'
            tmp_name = time.strftime("%Y%m%d-%H%M%S") + '.mp3'

            (
                ffmpeg
                .input(file_name)
                .output(tmp_name, map_metadata='0')
                .run()
            )

            # The file cannot be moved since it's across file systems.
            shutil.copyfile(tmp_name, new_file_name)
            os.remove(tmp_name)

            cursor: pymssql.Cursor = conn.cursor()
            cursor.execute('EXEC sp_UpdatePath %s, %s', (file_name, new_file_name))
            cursor.close()

            self.handle_duplicate_files(file_name)

            return new_file_name, True
            

        return file_name, True
