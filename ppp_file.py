import os


def get_folder(path):
    dirs = []
    files = []
    for name in os.listdir(path):
        (dirs if os.path.isdir(os.path.join(path, name)) else files).append(name)
    return sorted(dirs), sorted([i for i in files if i[-4:] == '.mp3'])
