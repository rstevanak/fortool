from os import path, stat, listdir
from subprocess import check_output
from hashlib import md5


def get_metadata(filename, filesystem_root):
    """Returns metadata of file specified"""
    file_desc = stat(filename, follow_symlinks=False)
    art = {}
    art["atime"] = file_desc.st_atime
    art["mtime"] = file_desc.st_mtime
    art["ctime"] = file_desc.st_ctime
    art["permissions"] = file_desc.st_mode
    art["uid"] = file_desc.st_uid
    art["gid"] = file_desc.st_gid
    raw_filetype = check_output(['file', '-b', filename])
    art["filetype"] = raw_filetype.decode('UTF-8')

    # no use in computing hash for symlink or directory
    if not path.islink(filename) and not path.isdir(filename):
        m = md5()
        # splitting lines, in case file is too big for ram
        # there should not be a problem with newlines, as python
        for line in open(filename, 'rb'):
            m.update(line)
        art["md5"] = m.hexdigest()
    # TODO: creation time
    # TODO: maybe calculate hash of file?
    return art


def parse(filename, recursive=True):
    """Parses (optionally recursively) metadata of all containing files
    if given directory and only given file if given file. Does not follow
    symlinks"""

    # if there is already entry for abspath because of parsing from parent
    # directory, it will be overwritten by this, but they should be the same
    abspath = path.abspath(filename)
    artifacts = {abspath: get_metadata(abspath)}
    # parsing all children, if it is viable
    if not path.islink(abspath) and path.isdir(abspath):
        for subfile in listdir(abspath):
            subfilepath = path.join(abspath, subfile)
            artifacts[subfilepath] = get_metadata(subfilepath)
            # recursively sending to directory children
            if path.isdir(subfilepath) and recursive:
                artifacts.update(parse(subfilepath, True))
    return artifacts
