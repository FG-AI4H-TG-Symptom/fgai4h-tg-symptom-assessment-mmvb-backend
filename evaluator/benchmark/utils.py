import os


def create_dirs(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
