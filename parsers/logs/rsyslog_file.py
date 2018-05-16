def parse(filename, filesystem_root):
    """Parses logfile, if the file is of usual format"""
    lines = []
    with open(filename, 'r') as file:
        for row in file:
            lines.append(parse_line(row))
    # TODO: parse log format from rsyslog.conf?
    artifacts = {filename: lines}
    return artifacts


def parse_line(line):
    words = line.split(" ")
    return {"timestamp": " ".join(words[:3]),
            "hostname": words[3],
            # to remove colon
            "tag": words[4][:-1],
            "message": " ".join(words[5:]),
            }
