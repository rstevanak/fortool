import os


def get_artifact(file, art_type=""):
    """Returns artifact about file containing mac times, with
    optional art_type argument, that appends to artifact type"""
    file_desc = os.stat(file)
    art_time = int(file_desc.st_atime//1)
    time_types = ["st_atime", "st_mtime", "st_ctime"]
    desc_vars = [file]+[getattr(file_desc, x) for x in time_types]
    art_desc = "File {} was last accessed {}, last modified {}, " \
               "metadata last changed {}".format(*desc_vars)
    # TODO: not to resolve symlinks
    # TODO: change desc depending on file type
    # TODO: users
    # TODO: creation time
    # TODO: maybe calculate hash of file?
    return art_time, "file"+str(art_type), art_desc


def parse(filename, art_type="", recursive=True):
    """Parses (optionally recursively) metadata of all containing files
    if given directory and only given file if given file"""
    artifacts = set()
    folder = os.path.abspath(filename)
    if not os.path.isdir(folder):
        return artifacts
    for file in os.listdir(folder):
        absolute_file = os.path.join(folder, file)
        artifacts.add(get_artifact(absolute_file, art_type))
        if os.path.isdir(absolute_file) and recursive:
            artifacts |= parse(absolute_file, art_type, True)
    return artifacts
