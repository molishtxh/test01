import subprocess

# import os
# import sys
# import time
# import yaml
# import cnf_values_migration as yaml_migrate
# import hsslcm as pkg_handler

"""
helm3 history blrsyve3 -n jit |awk 'END{print $1}'
helm3 rollback blrsyve3 3 -n jit --timeout 20m
"""


def cnf_roll_back(control_ip: str, user: str, password: str, cnf_name: str, name_space: str):
    podName_cmd = "sshpass -p " + password + \
                  " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + user + \
                  "@" + control_ip + " helm3 history " + cnf_name + " -n " + name_space + "| awk 'END{print $1}'"
    print(podName_cmd)
    pp = subprocess.Popen(podName_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                          shell=True)
    output, err = pp.communicate()
    if output.decode().strip() == "":
        print("can't find any load, there's something wrong with parameters")
        return 1
    else:
        revision_id = output.decode().strip()
        podName_cmd = "sshpass -p " + password + \
                      " ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null " + user + \
                      "@" + control_ip + " helm3 rollback " + cnf_name + " " + revision_id + " -n " + name_space + \
                      " --timeout 20m"
        return 0

