import re
from glob import glob
from os import path


def parse(filename, filesystem_root):
    """Parses configuration file of logrotate"""
    artifacts = {'logfile': {}, 'directives': {}}
    # matches line that starts with / and if it contains { it contiues till }
    action_regex = r'^(/\S+)\s+(?:{([^}]+)})?'
    # matches all lines that start with word-char -- that means not with
    # / or #, and all directives should start with word-char
    directive_regex = r'(\w+)(?:[ \t]+(\S+))*'
    logrot_files = [filename]
    for logrot in logrot_files:
        with open(logrot, 'r') as f:
            actions = re.findall(action_regex, f.read(), re.MULTILINE)
            f.seek(0)
            directives = re.findall(directive_regex, f.read(), re.MULTILINE)
        for i in actions:
            loc_directives = {}
            for j in i[1].split('\n'):
                # to exclude empty lines
                line = j.strip()
                if line:
                    spl_line = line.split(maxsplit=1)
                    # if line has parameters
                    if len(spl_line) > 1:
                        value = spl_line[1]
                    else:
                        value = ''
                    loc_directives[spl_line[0]] = value
            artifacts['logfile'][i[0]] = loc_directives
        # TODO: wildcards in actions filenames
        directives = dict(directives)
        artifacts['directives'] = directives
        # extending more directive files
        if directives.get('include'):
            nextpath = directives.get('include')
            nextpath = path.join(filesystem_root, nextpath.lstrip('/'))
            if path.isdir(nextpath):
                logrot_files += glob(nextpath + "/*")
            else:
                logrot_files.append(nextpath)
    return artifacts
