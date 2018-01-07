import os


def get_artifact(filename):
    """Returns mac times of file"""
    file_desc = os.stat(filename)
    art = {}
    art["atime"] = file_desc.st_atime
    art["mtime"] = file_desc.st_mtime
    art["scime"] = file_desc.st_ctime
    # TODO: not to resolve symlinks
    # TODO: change desc depending on file type
    # TODO: users
    # TODO: creation time
    # TODO: maybe calculate hash of file?
    return art


def parse(filename, recursive=True):
    """Parses (optionally recursively) metadata of all containing files
    if given directory and only given file if given file"""
    artifacts = {}
    folder = os.path.abspath(filename)
    if not os.path.isdir(folder):
        return artifacts
    for file in os.listdir(folder):
        absolute_file = os.path.join(folder, file)
        artifacts[absolute_file] = get_artifact(absolute_file)
        if os.path.isdir(absolute_file) and recursive:
            artifacts.update(parse(absolute_file, True))
            # TODO: solve symlinks
    return artifacts
