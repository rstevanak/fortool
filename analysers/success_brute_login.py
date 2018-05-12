import json
import sys
from collections import deque, defaultdict
import click


def analyse(parsed, threshold=5, timeframe=600):
    """Analyses file parsed from filesystem for $unsuccessful continuous
    unsuccessful login tryouts followed by successful one all within
    $timeframe"""
    # Assurance against incomplete data
    login_data = parsed.get('login_data')
    if not login_data:
        sys.stderr.write('No login_data in parsed file')
        return []
    db_wtmp = login_data.get('wtmp')
    db_btmp = login_data.get('btmp')
    if not db_wtmp or not db_btmp:
        sys.stderr.write('No wtmp or btmp data')
        return []
    # parsing un- and successful logins into dictionary where key is username
    # and IP on which login was attempted and value is all login data
    all_succ = defaultdict(list)
    all_unsucc = defaultdict(list)
    # not the most transparent way to parse both un- and successful attempts
    # the same without code repeating
    for src_list, dst_dict in [(db_wtmp, all_succ), (db_btmp, all_unsucc)]:
        for entry in src_list['data']:
            dst_dict[(entry['username'], entry['ip'])].append(entry)
    # intersection of usernames and ips in both lists, because there is no use
    # in looking through logins in just one of them
    users_all = [x for x in all_unsucc if x in all_succ]

    output = []
    for username in users_all:
        # rename for clarity
        user_succ = all_succ[username]
        user_unsucc = all_unsucc[username]
        output += find_brute(user_succ, user_unsucc, threshold, timeframe)
    return output


def find_brute(user_succ, user_unsucc, threshold, timeframe):
    # sort both un- and succesful logins of user if needed
    for d in [user_succ, user_unsucc]:
        if not all(d[i]['time'] <= d[i + 1]['time'] for i in range(len(d) - 1)):
            d.sort(key=lambda key: key['time'])
    if not user_unsucc or not user_succ:
        return []
    # pointer to last checked item in successful
    c_succ = 0
    # list of logins to be included in bruteforce attack
    logins_queue = deque()
    # array of strings to be outputted
    output = []
    out_str = "Found bruteforce attack at {}, last unsuccessful logins:\n {}" \
              "\nsuccessful login: {}"
    # rewriting simple c-like for loop, so i can increase i_index inside loop
    i_index = 0
    while i_index < len(user_unsucc):
        # appending unsucc login i at the end of the queue and assuring
        # queue is not longer than timeframe and threshold of unsuccessful
        # logins that define bruteforce
        i = user_unsucc[i_index]
        logins_queue.append(i)

        while logins_queue[0]['time'] + timeframe < i['time'] or \
                len(logins_queue) > threshold:
            logins_queue.popleft()

        if len(logins_queue) >= threshold:
            # looking for successful login
            for c_succ in range(c_succ, len(user_succ)):
                succ_time = user_succ[c_succ]['time']
                last_unsucc_time = user_unsucc[-1]['time']
                last_in_timeframe = user_unsucc[0]['time'] + timeframe
                if last_unsucc_time <= succ_time <= last_in_timeframe:
                    # include all entries between last found in threshold and
                    # successful login
                    while ((i_index + 1) < len(user_unsucc) and
                           user_unsucc[i_index + 1]['time'] <= succ_time):
                        logins_queue.append(user_unsucc[i_index + 1])
                        i_index += 1
                    # making string for output
                    str_unsucc = ", \n".join([str(x) for x in logins_queue])
                    str_time = str(succ_time)
                    str_succ = str(user_succ[c_succ])
                    # TODO: better format
                    s = out_str.format(str_time, str_unsucc, str_succ)
                    output.append(s)
                # if successful login is later than in timeframe
                elif last_in_timeframe < succ_time:
                    # since it is broken, next time c_succ should be the first
                    # index to be checked out
                    break
        i_index += 1
    return output


@click.command()
@click.argument('filename', type=click.Path(exists=True, file_okay=True,
                                            dir_okay=False, readable=True))
@click.option('--threshold', '-r', default=5, type=int,
              help='Number of bad logins as a trigger')
@click.option('--timeframe', '-t', default=600, type=int,
              help='Timefrime, within which is considered attack')
def cli_analyse(filename, threshold, timeframe):
    with open(filename, 'r') as file:
        parsed = json.load(file)
    output = analyse(parsed, threshold, timeframe)
    for i in output:
        print(i)


if __name__ == '__main__':
    cli_analyse()
