import os
import pymssql
import time

from os import path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from steps.ConvertToMp3 import ConvertToMp3Step
from steps.Fingerprint import FingerprintStep
from steps.Acoustid import AcoustidStep
from steps.MusicBrainz import MusicBrainzStep
from steps.UpdateTags import UpdateTagsStep
from steps.Lyrics import LyricsStep
from steps.MoveFile import MoveFileStep

plugins = []
conn: pymssql.Connection = None

class WatchdogHandler(FileSystemEventHandler):
    def on_created(self, event):
        execute(event.src_path, conn)

def write_step(file_name: str, step_name: str, conn: pymssql.Connection):
    cursor: pymssql.Cursor = conn.cursor()
    cursor.execute(
        'EXEC sp_InsertLastStep %s, %s', (file_name, step_name))
    cursor.close()

def get_last_step(file_name: str, conn: pymssql.Connection) -> str:
    # Get all of the steps
    cursor: pymssql.Cursor = conn.cursor()
    cursor.execute(
        'EXEC sp_SelectSteps %s', (file_name)
    )
    # We only care about the most recent one.
    row = cursor.fetchone()
    cursor.close()

    if row is None:
        return None
    else:
        return row[0]

def get_files(directory):
    # Get all the files and directories in the specified folder.
    struct = [path.join(directory, f) for f in os.listdir(directory)]

    # Get the files in subdirectories.
    dir_files = [get_files(s) for s in struct if path.isdir(s)]
    # Flatten the list of lists.
    dir_files_flat = [item for sublist in dir_files for item in sublist]
    # Get the files for this folder.
    files = [s for s in struct if path.isfile(s)]

    # Merge all the files found.
    result = files + dir_files_flat

    return result

def main():
    global plugins
    global conn

    # Get secrets from env variables
    server = os.environ['DATABASE_HOST_NAME']
    user = os.environ['DATABASE_USER']
    password = os.environ['DATABASE_PASSWORD']
    database_name = os.environ['DATABASE_NAME']

    conn = pymssql.connect(server, user, password, database_name, autocommit=True)

    plugins = [
        FingerprintStep(),
        ConvertToMp3Step(),
        AcoustidStep(),
        MusicBrainzStep(),
        UpdateTagsStep(),
        LyricsStep(),
        MoveFileStep()
    ]
    plugins.sort(key=lambda x: x.priority)

    path = './shares/music-upload'

    # We use a file system watcher to pick up added music files.
    event_handler = WatchdogHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    # Organize the files that are already in the music upload folder.
    files = get_files(path)
    for file in files:
        execute(file, conn)

    # Spin-lock for file system watcher.
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

    # Clean-up SQL connection.
    conn.close()

def execute(file: str, conn: pymssql.Connection):
    global plugins

    # Get the last step executed for the current file,
    # this allows us to continue from where we left off.
    file_plugins = plugins
    last_step = get_last_step(file, conn)

    # Remove the steps we've already executed.
    if last_step is not None:
        last_priority = [p for p in plugins if p.step_name == last_step][0].priority
        file_plugins = [p for p in plugins if p.priority > last_priority]

    for plugin in file_plugins:
        # Update the file name.
        file, should_continue = plugin.execute(file, conn)

        # Break if the previous step indicated we should stop.
        if should_continue:
            # Write the log of the step
            write_step(file, plugin.step_name, conn)
        else:
            break


if __name__ == '__main__':
    main()
