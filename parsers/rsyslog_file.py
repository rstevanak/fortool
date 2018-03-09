def parse(filename):
    """Parses logfile, if the file is of usual format"""
    lines = []
    with open(filename, 'r') as file:
        for row in file:
            lines.append(parse_line(row))
    # TODO: parse log format from rsyslog.conf?
    artifacts = {filename: lines}
    return artifacts


def parse_line(line):
    art = {}
    words = line.split(" ")
    art["timestamp"] = " ".join(words[:3])
    art["hostname"] = words[3]
    art["tag"] = words[4][:-1]  # to remove colon?
    # TODO: maybe parse pid
    art["message"] = " ".join(words[5:])
    return art
