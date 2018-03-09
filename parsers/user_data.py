from os import path


def parse(filename):
    """"Parses usernames, their homes and shells, given
    /etc and also its password hash and expiratory
    information"""
    # TODO: somehow refactor, so user can specify location of shadow
    # and passwd explicitly
    # TODO: sudoers, groups
    artifacts = {}

    passwd = path.join(path.abspath(filename), "passwd")
    shadow = path.join(path.abspath(filename), "shadow")

    art_passwd = parse_passwd(passwd)
    art_shadow = parse_shadow(shadow)
    # merging data from passwd and shadow

    # done this way, just in case some user was uncorrectly deleted
    users = art_passwd.keys() | art_shadow.keys()
    for user in users:
        artifacts[user] = art_passwd[user]
        artifacts[user].update(art_shadow[user])
    return artifacts


def parse_shadow(filename):
    """Parses expiry info and password hashes to users from provided
    shadow file"""
    artifact = {}
    with open(filename, 'r') as passfile:
        for line in passfile:
            words = line.split(":")
            artifact[words[0]] = {}
            user = artifact[words[0]]
            user["pass_hash"], user["pass_age"] = words[1:3]
            user["pass_min_age"], user["pass_max_age"] = words[3:5]
            user["pass_warn_before_expiry"] = words[5]
            user["pass_disable_after_expiry"] = words[6]
            user["pass_disabled_since"] = words[7]
    return artifact


def parse_passwd(filename):
    """Parses usernames, homes, shells and ids from provided passwd file"""
    artifact = {}
    with open(filename, 'r') as passfile:
        for line in passfile:
            words = line.split(":")
            artifact[words[0]] = {}
            user = artifact[words[0]]
            user["info"], user["home"], user["shell"] = words[4:7]
            user["uid"], user["main_gid"] = words[2:4]
    return artifact

