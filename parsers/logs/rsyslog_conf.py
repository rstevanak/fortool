import re
import sys
from glob import glob
from os import path

from parsers.logs import rsyslog_file


def parse(filename, filesystem_root):
    """Parses all log files and settings given rsyslog.conf"""
    artifacts = {
        'meta': {
            'directives': {},
            'actions': {},
            'rainerscripts': []
        },
        'logfiles': {}
    }

    lines = conf2lines(filename)
    # TODO: new configuration format
    for line in lines:
        # ignore module loading
        if line.startswith('module('):
            continue
        # this is in case of directives
        elif line.startswith('$'):
            splt = line.split(maxsplit=1)
            artifacts['meta']['directives'][splt[0][1:]] = splt[1]

            # in case this directive extends rsyslog with some files
            if splt[0] == "$IncludeConfig":
                abs_wild = path.join(filesystem_root, splt[1].lstrip('/'))
                for ext_file in glob(abs_wild):
                    lines += conf2lines(ext_file)
        # in case of RainerScript
        elif line.startswith('if '):
            artifacts['meta']['rainerscripts'].append(line)
        # if it is in syntax "filter action":
        # in case of property based filter
        elif line.startswith(':'):
            # syntax should be :PROPERTY, [!]COMPARE_OPERATION, "STRING"
            m = re.match(r'(:\w+,\W*!?\w+,\W*"[^"]+")\s*(.+)', line)
            log_filter, log_action = m.groups()
            artifacts['meta']['actions'][log_filter] = log_action
        else:
            # syntax should be Facility.priority
            spl = line.split(maxsplit=1)
            artifacts['meta']['actions'][spl[0]] = spl[1]

    # TODO: parse format from config
    # TODO: parse templates
    # parsing log files read from configuration
    for logfile in artifacts['meta']['actions'].values():
        # paths can begin with - @ for sending over network
        # : for passing information to previously defined $outchannel
        # ^ for script execution
        # - to disable syncing
        # / for file path, all have to be in absolute path
        if logfile[0] == '-':
            logfile = logfile[1:]
        if logfile[0] == '/':
            abslog = path.join(filesystem_root, logfile[1:])
            if not path.exists(abslog):
                sys.stderr.write("No file at {}, skipping\n".format(abslog))
                continue
            rsys_parsed = rsyslog_file.parse(abslog, filesystem_root)
            artifacts['logfiles'][abslog] = rsys_parsed
    return artifacts


def conf2lines(filename):
    lines = []
    with open(filename, 'r') as f:
        for line in f:
            # in config, when line ends with \ it is treated as if no newline
            # appeared
            while line.endswith('\\\n'):
                line = line[:-2] + f.readline().lstrip()
            # strip newline
            line = line.strip()
            # ignore comments and empty lines
            if line and not line.startswith('#'):
                lines.append(line)
    return lines
