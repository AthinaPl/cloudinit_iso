#!/usr/bin/env python3

import subprocess
import argparse
import yaml
import crypt
import random
import string


####################################################################
# This is a script that creates an ISO image for cloud init config #
####################################################################


try:
    from secrets import choice as randchoice
except ImportError:
    from random import SystemRandom
    randchoice = SystemRandom().choice


def sha512_crypt(password, salt=None, rounds=None): 

    # Hash creation of given password, needed by cloud-init for user-data file.
    #Similar output to mkpasswd, which is recommended in cloud-init documentation.
    if salt is None:
        salt = ''.join([randchoice(string.ascii_letters + string.digits)
                        for _ in range(8)])

    prefix = '$6$'
    if rounds is not None:
        rounds = max(1000, min(999999999, rounds or 5000))
        prefix += 'rounds={0}$'.format(rounds)

    return crypt.crypt(password, prefix + salt)


def input_args(): 

    # Input arguments parsing
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "-n", "--name", required=True,
            help="The default user's name, required. It will also be used for localhost declaration")
    parser.add_argument(
            "-p", "--passwd",
            help="Password for default user. It is not required but strongly recommended")

    args = parser.parse_args()

    return args


def create_metadata(localname):

    instance = localname+str(random.randint(1,2000))
    # used random to produce unique id based on the localhost name 
    
    with open("meta-data", "w+") as f:
        yaml.dump({'instance-id': instance, 'local-hostname': localname}, f)
        f.close()

    return f


def create_userdata(username, password=None):
    
    #Presuming for the moment that user always provides password
    if password:
        pw = sha512_crypt(password, rounds=4096)
        print(pw)
    
    userdata_dictionary = {
        'groups': [{
            'ubuntu': 'root, sys'},
            'cloud-users'
            ],
        'users': [
            'default',
            {'name': username,
            'groups': 'users, admin',
            'sudo': 'ALL=(ALL) NOPASSWD:ALL',
            'ssh_import_id': 'None',
            'lock_passwd': 'false',
            'passwd': pw
            }]
        }

    with open("user-data", "w+") as f:
        yaml.dump(userdata_dictionary, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    f.close()

    return f


def generate_iso(name, passwd=None):

    mt = create_metadata(name)
    ur = create_userdata(name, passwd)
#    iso_name = 'config.iso'
#    cmd = ["genisoimage", "-o",
#            "{0}".format(iso_name),
#            "-V", "cidata", "-r", "-J",
#            "{0}".format(mt),
#            "{0}".format(ur)]
    cmd = 'genisoimage -o config.iso -V cidata -r -J' + mt + ur
    subprocess.call(cmd, shell=True)


    return


if __name__ == '__main__':

    args = input_args()
    generate_iso(args.name, args.passwd)
