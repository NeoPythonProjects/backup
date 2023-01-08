import os
import stat
from time import ctime

import platformdirs
from kivy.utils import platform

def test_last_modified():
    # Get last modification time of a file
    # Retrieve home directory from environment variables
    home_dir = os.environ['HOME']
    # for portability, don't concatenate with / but use os.path.join()
    file_path = os.path.join(home_dir, 'log_updates.txt')
    # create results object
    results_object = os.stat(file_path)
    # retrieve access time property from this object in seconds, and convert to time
    # Python time method ctime() converts a time expressed in seconds since the epoch
    # to a string representing local time
    # access the results object using [] as it it were a dictionary
    last_mod_time = ctime(results_object[stat.ST_MTIME])
    return last_mod_time


def test_replace():
    # only changes the file name, not the content
    os.replace('./test_backup/original_v2.txt', './test_backup/newversion.txt')



if __name__ == '__main__':
    print(platformdirs.PlatformDirs)
    print(platform)
