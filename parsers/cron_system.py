import re
from os.path import abspath, join, isdir, dirname, islink
from os import listdir


def parse(filename):
    """Parses etc/crontab ,its cron.d and also hourly, daily and monthly"""
    artifacts = {"jobs":[]}
    artifacts["jobs"] = parse_crontab(filename)

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
    cron_pattern = r'(([0-9]{1,2}|\*|\*/[0-9]+)\s){5}\w+\s.+'

    cron_file = open(filename, 'r')
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
    cron_file.close()
    return jobs


def parse_cron_dict(filename):
    """Returns dictionary of format filename:contents_of_file,
    given directory"""
    jobs = {}
    abs_path = abspath(filename)
    if not isdir(abs_path):
        return []
    for file_script in listdir(abs_path):
        path_script = join(abs_path, file_script)
        # temporary skipping of symlinks
        # TODO: solve what to do with symlinks
        if islink(path_script):
            continue
        with open(path_script, 'r') as f:
            jobs[file_script] = f.read()
    return jobs
