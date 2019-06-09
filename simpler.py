#!/usr/bin/env python3

import subprocess
import argparse
import yaml
import random
import string


####################################################################
# This is a script that creates an ISO image for cloud init config #
####################################################################


def input_args(): 

    # Input arguments parsing
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "-n", "--name",
            help="The default user's name, required. It will also be used for localhost declaration")
    parser.add_argument(
            "-p", "--passwd",
            help="Password for default user. It is not required but strongly recommended")

    args = parser.parse_args()

    return args


def create_metadata(localname=None):

    if localname:
        instance = localname+str(random.randint(1,2000))
        # used random to produce unique id based on the localhost name 
    else:
        localname = instance = "instance"+str(random.randint(1,2000))

    file_name = "meta-data"

    with open(file_name, "w") as f:
        yaml.dump({'instance-id': instance, 'local-hostname': localname}, f)

    return file_name


def create_userdata(username=None, password=None):
   
    if not password:
        password = "password"

    userdata_dictionary = {
            'password': password
            }

    file_name = "user-data"
    with open(file_name, "w+") as f:
        f.write("#cloud-config\n")
        if username:
            yaml.dump({'name': username}, f)
        yaml.dump(userdata_dictionary, f, allow_unicode=True,
                default_flow_style=False, sort_keys=False)
        f.writelines(["chpasswd: { expire: False }\n", "runcmd:\n", "- [ sudo, touch, /etc/cloud/cloud-init.disabled ]"])

    return file_name


def generate_iso(name, passwd=None):

    mt = create_metadata(name)
    ur = create_userdata(name, passwd)
    iso_name = 'config.iso'
    cmd = ['genisoimage', '-o', iso_name, '-V', 'cidata', '-r', '-J', mt, ur]
    subprocess.call(cmd)

    return


if __name__ == '__main__':

    args = input_args()
    generate_iso(args.name, args.passwd)
