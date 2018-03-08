import os


def get_metadata(filename):
    """Returns metadata of file specified"""
    file_desc = os.stat(filename, follow_symlinks=False)
    art = {}
    art["atime"] = file_desc.st_atime
    art["mtime"] = file_desc.st_mtime
    art["ctime"] = file_desc.st_ctime
    art["permissions"] = file_desc.st_mode
    art["uid"] = file_desc.st_uid
    art["gid"] = file_desc.st_gid
    # TODO: change desc depending on file type
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
        artifacts[absolute_file] = get_metadata(absolute_file)
        if os.path.isdir(absolute_file) and recursive:
            artifacts.update(parse(absolute_file, True))
    return artifacts
