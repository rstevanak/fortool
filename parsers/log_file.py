import time


def parse(filename):
    artifacts = set()
    with open(filename, 'r') as file:
        for row in file:
            art_time = " ".join(row.split()[:3])
            art_desc = " ".join(row.split()[3:])
            artifacts.add((art_time, "log", art_desc))
    # TODO: time into epoch(missing year?)
    # TODO: parse contents of log
    # TODO: parse logs from format in rsyslog.conf?
    return artifacts

def parse_line(line):
    art = {}
    words = line.split(" ")
    month = time.strptime(words[0], "%b").tm_mon
    art["timestamp"] = " ".join(words[:3])
    art["hostname"] = words[3]
    art["tag"] = words[4][:-1] # to remove colon?
    # TODO: should it parse pid, since it is only a convention and it could
    # lead to intentional tampering?
    art["message"] = " ".join(words[5:])
    return art
