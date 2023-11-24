import subprocess
from local_settings import STORAGE_PATH


def ladu_folder_exists(dirname):
    return dirname in list(map(lambda x: x[:-1], subprocess.check_output(["mc", "ls", STORAGE_PATH]).split()[4::5]))


def ladu_file_exists(filename, dirname):
    return filename in list(map(lambda x: x[:-1],
                                subprocess.check_output(["mc", "ls", STORAGE_PATH + "/" + dirname]).split()[4::5]))


def ladu_create_folder(dirname):
    subprocess.call(["mc", "mb", "{0}/{1}".format(STORAGE_PATH, dirname)])


def ladu_move_file_to_storage(file_path, storage_path):
    subprocess.call(["mc", "mv", file_path, "{0}/{1}".format(STORAGE_PATH, storage_path)])


def ladu_copy_file_from_storage(file_path, destination_path):
    print("moving from {0} to {1}".format(file_path, destination_path))
    subprocess.call(["mc", "cp", "{0}/{1}".format(STORAGE_PATH, file_path), destination_path])


# Do NOT use to write b'', pure strings only!
def ladu_write_file(content, file_path):
    subprocess.call('echo "{0}" | mc pipe {1}/{2}'.format(content, STORAGE_PATH, file_path), shell=True)
