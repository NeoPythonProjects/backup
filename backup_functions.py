# gui
# input: source and destination directories
import os
import stat
import time
import datetime
import filecmp
from pathlib import Path
import kivy

def last_modified_string(filepath: str) -> str:
    # NOT USED
    # Get last modification time of a file
    # Create results object os.stat(filepath)
    # Retrieve access time property from this object in seconds, and convert to time
    # Python time method ctime() converts a time expressed in seconds since the epoch
    #   to a string representing local time
    return time.ctime(os.stat(filepath)[stat.ST_MTIME])


def last_modified_date_time(filepath: str) -> list:
    # NOT USED
    last_modified_since_epoch_seconds = os.path.getmtime(filepath)
    # convert to struct_time
    last_modified_time = time.localtime(last_modified_since_epoch_seconds)
    return [time.strftime('%Y-%m-%d', last_modified_time),
            time.strftime('%H:%M:%S', last_modified_time)]


def last_modified_struct_time(filepath: str) -> time:
    last_modified_since_epoch_seconds = os.path.getmtime(filepath)
    # convert to struct_time using localtime()
    # __repr__ of this struct_time gives:
    # time.struct_time(tm_year=2022, tm_mon=12, tm_mday=17, tm_hour=21,
    # tm_min=0, tm_sec=19, tm_wday=5, tm_yday=351, tm_isdst=0)
    # so can be accessed via .tm_year etc
    # print(last_modified_struct_time('/home/xubuntu/log_updates.txt').tm_year)
    # gives 2022
    # struct_time can be compared directly:
    # last_modified_struct_time(file1) > last_modified_struct_time(file2)
    return time.localtime(last_modified_since_epoch_seconds)


def load_file_list(path: str) -> list:
    # os.listdir('dir_path'): Return the list of files and directories present in a specified directory path.
    # os.walk('dir_path'): Recursively gets the list of all files in directory and subdirectories.
    # os.scandir('path'): Returns directory entries along with file attribute information.
    # glob.glob('pattern'): glob module to list files and folders whose names follow a specific pattern.
    file_list = []
    # leave for loop in notes for nice list comprehendion example
    # for f in os.listdir(path):
    #     if os.path.isfile(os.path.join(path, f)):
    #         # appends the filename only
    #         file_list.append(f)
    file_list = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    # file_list include all hidden files, starting with a .
    # return a list comprehension of filenames that excludes those files
    return [f for f in file_list if not f.startswith('.')]


def load_folder_list_recursive(path: str) -> list:
    result = []
    for (path, subpath, file) in os.walk(path):
        # path is a string
        # subpath is a list with all the sub folders of path
        # we can ignore subpath, as os.walk goes through al sub folders
        # so every folder and sub folder will show up as path at some point
        # example:
        # print(path)
        # print(subpath)
        # example output:
        # / home / xubuntu / PycharmProjects / backup / test_backup
        # ['test_backup_L2', 'test_backup_L2_folder2']
        # / home / xubuntu / PycharmProjects / backup / test_backup / test_backup_L2
        # ['test_backup_L3', 'test_backup_L3_folder2']
        # / home / xubuntu / PycharmProjects / backup / test_backup / test_backup_L2 / test_backup_L3
        # []
        # / home / xubuntu / PycharmProjects / backup / test_backup / test_backup_L2 / test_backup_L3_folder2
        # []
        # / home / xubuntu / PycharmProjects / backup / test_backup / test_backup_L2_folder2
        # []
        # []
        # append an entire iterable at end of another iterable via extend
        # that appends each character as a list element
        # I need to append each path string as one element
        # just append
        result.append(path)
        # return a list of folder paths
        # we need this because we can use each list element as source in compare_directories
    return result


def compare_directories(source: str, destination: str) -> tuple:
    # ***********************************
    # * does not look at subdirectories *
    # ***********************************
    # recursion is performed before this function is triggered
    # in load_folder_list_recursive
    # list of files to be compared within the 2 directories only
    # read in filenames in source directory
    files = load_file_list(source)
    # unpacking the tuple
    # match, mismatch, errors = filecmp.cmpfiles(source, destination, files, shallow=True)
    # comparison on filename means that:
    # match: filename exists in both directories and has the same properties in both directories
    # mismatch: filename exists in both directories but has at least one property differ between directories
    # error: filename does not exist in backup directory (it might exist in another directory
    # but we're only checking in the selected folder of the backup folder)
    return filecmp.cmpfiles(source, destination, files, shallow=True)


def more_recent_files(mismatch: list, source: str, destination: str) -> list:
    # for each file in the mismatch list compare last modified date in source and destination
    # source directory is the user's chosen home directory or similar
    # destination directory is the user's chosen back up folder
    source_dates = [last_modified_struct_time((os.path.join(source, f))) for f in mismatch]
    destination_dates = [last_modified_struct_time((os.path.join(destination, f))) for f in mismatch]
    # zip 3 lists together into 1 list of tuples holding elements of each list:
    # zip(a,b, c) = [(a1, b1, c1),(a2, b2, c2)...]
    # check if there are any backups that are more recent than the file the user is trying to back up
    more_recent_backups = [f for f, source_date, destination_date in
                           zip(mismatch, source_dates, destination_dates) if source_date < destination_date]
    if more_recent_backups:
        action_more_recent_backup(more_recent_backups)

    # return a list of file_paths where the user's file is more recent than the backups
    return [f for f, source_date, destination_date in
            zip(mismatch, source_dates, destination_dates) if source_date > destination_date]


def new_files(errors: list, source: str) -> list:
    # files in the source directory that are not in back up directory
    # show up as errors
    return errors


def replace_one_file(out_of_date_file_path: str, recent_file_path: str) -> None:
    # replacing a file, or updating a file, means deleting the data in the source
    # file and writing the data from the new file
    # store new file content in variable
    with open(recent_file_path, 'rb') as f_recent:
        new_content = f_recent.readlines()
    # open() automatically creates the file if it doesn't exist but only if the folder exists
    # if the folder doesn't exist, open() of course doesn't create the folder, but crashes
    # so create folder first if it doesn't exist
    # out_of_date_file_path includes filename
    # remove that by taking off the tail
    # split results in tuple(head, tail)
    folder_to_check, filename = os.path.split(out_of_date_file_path)
    if not os.path.exists(folder_to_check):
        # os.mkdir(folder_to_check)
        # create parent folders if they don't exist; loop doesn't follow top down tree structure
        Path(folder_to_check).mkdir(parents=True)
    # the folder now exists, so open() will create the file if it doesn't exist
    with open(out_of_date_file_path, 'wb') as f_source:
        f_source.writelines(new_content)


def replace_files(more_recent_files_list: list, source_dir: str, destination_dir: str) -> None:
    source_files = [os.path.join(source_dir, f) for f in more_recent_files_list]
    destination_files = [os.path.join(destination_dir, f) for f in more_recent_files_list]
    # enumerate allows you to loop over an iterable, with index available
    # zip creates an iterable of tuples
    for index, el in enumerate(zip(source_files, destination_files)):
        # alternatively: for src, dest in zip(source_files, destination_file):
        # print(f"new file that will survive {el[0]}")
        # print(f"old file that will be deleted {el[1]}")
        # replace file in second element of tuple el[1] by file in first element of tuple el[0]
        replace_one_file(el[1], el[0])
        # el[0] sits in the source directory, the user's home directory for example; that's the mor recent
        # el[1] sits in the backup directory; that's out of date
        log(f"back up: {el[1]}")


def log(content: str) -> None:
    log_entry = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S") + " >> " + content + "\n"
    # add to permanent log
    with open('backup_log.txt', 'a') as log_file:
        log_file.write(log_entry)
    # add to recent log to be shown on label'
    with open('backup_log_recent.txt', 'a') as f:
        f.write(log_entry)


def action_more_recent_backup(file_path_list: list) -> None:
    for el in file_path_list:
        log(f"back up {el} is more recent. Please check.")


def save_backup_date() -> str:
    current_datetime = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
    with open('files/most_recent_backup.txt', 'w') as f:
        f.write(current_datetime)
    return current_datetime


def replace_source_dir(path, source_dir, dest_dir):
    # find the first instance of source_dir on path
    # find by definition finds the first instance only
    # this will be index 0 or 1, depending on whether anything sits in front
    # but we can actually ignore this because:
    # replace by default replaces all instances, but can be set to count=1 to only
    # replace the first one
    return path.replace(source_dir, dest_dir, 1)


def start(source_dir, destination_dir):
    # test directories
    # -----------------
    # source_dir = os.path.join(os.environ['HOME'], "PycharmProjects", "backup", "test_backup")
    # destination_dir = os.path.join(os.environ['HOME'], "PycharmProjects", "backup", "test_backup", "backup_here")
    # ----- end --------
    # with the source_dir as home, find all sub folders and list them
    home_folder_list = load_folder_list_recursive(source_dir)
    # create destination folders from home_folder_list
    # replace first instance of source_dir with destination_dir in home_folder_list
    backup_folder_list = [replace_source_dir(path, source_dir, destination_dir) for path in home_folder_list]
    for source_dir, destination_dir in zip(home_folder_list, backup_folder_list):
        files_list = []
        match, mismatch, errors = compare_directories(source_dir, destination_dir)
        files_list = more_recent_files(mismatch, source_dir, destination_dir)
        files_list.extend(new_files(errors, source_dir))
        replace_files(files_list, source_dir, destination_dir)
    save_backup_date()


if __name__ == '__main__':
    pass
    # start()
    # test directories
    # -----------------
    # source_dir = os.path.join(os.environ['HOME'], "PycharmProjects", "backup", "test_backup")
    # destination_dir = os.path.join(os.environ['HOME'], "PycharmProjects", "backup", "backup_here")
    # # ----- end --------
