import re
from os.path import abspath, join, dirname
from os import listdir


def parse(filename, filesystem_root):
    """Parses etc/crontab ,its cron.d and also hourly, daily and monthly"""
    artifacts = {"jobs": parse_crontab(filename)}

    # parsing every file from ./cron.d/ as crontab
    crond_dir = abspath(join(dirname(filename), "cron.d"))
    for crond_tab in listdir(crond_dir):
        artifacts["jobs"] += parse_crontab(join(crond_dir, crond_tab))

    # TODO: maybe parse directories names out of crontab
    # for time in ['daily', 'weekly', 'monthly']:
    #     cron_dir = join(dirname(filename), 'cron.' + time)
    #     artifacts[time + "_jobs"] = parse_cron_dict(cron_dir)
    return artifacts


def parse_crontab(filename):
    """Parses /etc/crontab or file of this format, returns array of jobs"""
    jobs = []
    # this is the line we want to be matched
    # TODO: maybe rewrite regex to use groups and be more readable
    cron_pattern = r'(([0-9]{1,2}|\*|\*/[0-9]+)\s){5}\w+\s.+'

    with open(filename, 'r') as cron_file:
        for line in cron_file:
            sline = line.lstrip()
            # skip commentaries and empty lines
            if not sline or sline[0] == '#':
                continue
            # TODO: parse SHELL and PATH directives
            if re.match(cron_pattern, sline, ):
                job = {}
                words = line.split()
                job["cron_time"] = " ".join(words[:5])
                job["job"] = " ".join(words[6:])
                job["run_as_user"] = words[5]
                jobs.append(job.copy())
    return jobs
