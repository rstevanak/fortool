import json
import re
import sys


# TODO: refactor this module
def analyse(parsed, conf_file='analysers/timeline.conf'):
    # matches nonwhitespace "whatever" everything_until_endofline
    line_regex = r"^(\S+)\s+\"([^\"]*)\"\s+([^$]+)$"
    commands = []
    # parsing commands from conf file
    with open(conf_file, 'r') as conf:
        for line in conf:
            # skipping comments
            if line.strip().startswith('#'):
                continue
            m = re.match(line_regex, line)
            if m:
                commands.append(m.groups())
    # list of tuples to be outputted
    final_entries = []
    for comm in commands:
        extr_path = comm[0].split('.')
        # string to be formatted
        out_str = comm[1]
        # paths to parameters to be formatted into out_str
        out_params_paths = [x.strip() for x in comm[2].split(',')]

        # TODO: maybe make two lists into list of tuples
        # this will be the list of values, with all wildcards subsituted
        values = [parsed]
        # this will be the list of string paths corresponding to values
        # it is list of lists of strings and ints for effectiveness
        values_paths = [[]]

        for key in extr_path:
            # added, so we don't iterate through changing list
            newvalues = []
            newvalues_paths = []

            # if there is a wildcard
            if key == '*':
                # iterating through indexes
                for i in range(len(values)):
                    # creating list of keys or indexes to iterate through
                    if isinstance(values[i], list):
                        it = list(range(len(values[i])))
                    elif isinstance(values[i], dict):
                        it = list(values[i].keys())
                    else:
                        raise TypeError

                    for wild_sub in it:
                        newvalues.append(values[i][wild_sub])
                        newvalues_paths.append(values_paths[i] + [wild_sub])
            # if there is no wildcard
            else:
                for i in range(len(values)):
                    try:
                        newvalues.append(values[i][key])
                        newvalues_paths.append(values_paths[i] + [key])
                    except KeyError:
                        sys.stderr.write("No key {} at {}, skipping command"
                                         "\n".format(key, values_paths[i]))
            values = newvalues
            values_paths = newvalues_paths
        # at this point, list values represent times by which entries should
        # be sorted, and values_paths represent path to them

        for i in range(len(values)):
            # in this field out_params_paths will be substituted for their
            # values
            out_params = []
            # this is path to time from which we want to substitute *
            time_path = values_paths[i]

            for p in out_params_paths:
                out_params.append(get_parameter(p, time_path, parsed))
            # Now composition of final entry

            entry = (values[i], out_str.format(*out_params))

            final_entries.append(entry)
    # sorting entries by time
    final_entries.sort(key=lambda x: x[0])
    return final_entries


def get_parameter(param_path, template_path, db):
    """returns string value of parameter, given its path, which can contain
    wildcards,template path, from which wildcards will be substituted and
    structure, from which it should be fetched"""
    # path to parameter to be built
    path = []
    # TODO optimize this
    if param_path.startswith('.'):
        path = template_path[:-1] + [param_path[1:]]
    else:
        paths_diverged = False
        all_steps = param_path.split('.')
        for j in range(len(all_steps)):
            step = all_steps[j]
            # we need to substitute all asterisks for their values
            if step == '*':
                if not paths_diverged:
                    path.append(template_path[j])
                else:
                    sys.stderr.write("""
                    Paths already diverged,wildcard cant be 
                    substituted {}""".format(path))
            # special case if we want to return key not value of dict
            # only for assurance that ^ is at the end and paths has not
            # diverged
            elif step == '^':
                if j == len(all_steps) - 1 and not paths_diverged:
                    path.append('^')
                else:
                    sys.stderr.write("""
                    Paths already diverged or ^ in parameter path\n""")
            else:
                if step != template_path[j]:
                    paths_diverged = True
                path.append(step)
    # now we get value for built path
    val = db
    for i in range(len(path)):
        step = path[i]
        if step == '^':
            val = template_path[i]
        else:
            val = val[step]
    return str(val)
