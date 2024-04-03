#!/usr/bin/python

import os
import sys
import getpass
import json
import argparse
import collections
import subprocess
HSS_USER_JSON = """{
  "users": [
    {
      "username": "hssuser",
      "password": "",
      "group": ["ldapgroup"],
      "uid": "5005",
      "gid": ["2009"],
      "homedir": "/home/hssuser",
      "shell": "/bin/bash"
    },
    {
      "username": "epsuser",
      "password": "",
      "group": ["ldapgroup"],
      "uid": "5006",
      "gid": ["2009"],
      "homedir": "/home/epsuser",
      "shell": "/bin/bash"
    },
    {
      "username": "hlruser",
      "password": "",
      "group": ["ldapgroup"],
      "uid": "5007",
      "gid": ["2009"],
      "homedir": "/home/hlruser",
      "shell": "/bin/bash"
    }
  ]
}
"""

class Logger(object):
    def __init__(self, fileN="Default.log"):
        self.terminal = sys.stdout
        self.log = open(fileN, "a")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        pass

def updateUserFiles(path, hssPasswd, neType):
    if neType == "sdl":
        hssUserFile = path + "sdlcnf_hssuser.json"
        hssUserData = open(hssUserFile, "w")
        hssUserData.write(HSS_USER_JSON)
        hssUserData.close()
    for jsonfile in os.listdir(path):
        print(jsonfile)
        updateUserFile(path + jsonfile, 'QN%Sn8jn')
    if neType == "sdl":
        updateUserFile(hssUserFile, hssPasswd)

def updateUserFile(jsonfile, password):
    print("updateUserFile is " + jsonfile)
    if (os.path.isfile(jsonfile)) and (".json" in jsonfile):
        print("======it is json file is: " + jsonfile)
        manifest_config = json.load(open(jsonfile), object_pairs_hook=collections.OrderedDict)
        if "users" not in manifest_config:
            return
        for item in manifest_config["users"]:
            item["password"] = password
        with open(jsonfile, "w") as jsonFile:
            jsonFile.write(json.dumps(manifest_config, indent = 2))

def createRealm(path, ztsIP, umpassword, neType):
    commonStr = path + "/createLinuxRealm.sh "+ ztsIP + " 9090 "
    commandList = []
    if neType == "sdl":
        command1 = commonStr + "sdl_default_realm admin " + umpassword + " true"
        command2 = commonStr + "sdl_db_realm  admin " + umpassword +  " true"
        commandList = [command1, command2]
    else:
        command3 = commonStr + "pgw_default_realm  admin " + umpassword + " true"
        commandList = [command3]
    for command in commandList:
        print("command is" + command)
        p1 = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        output, err = p1.communicate()
        err = err.decode()
        output = output.decode()
        
        print("output:" + output)
        if "successfully" not in str(output.strip()):
            print("output:" + output + " err: " + err)
            print("command:" + command + " , run failed with error:" + err)
            sys.exit(1)

def provisionUM(path, ztsIP, umpassword, neType):
    commonStr = path + "um_provisioner -o add -host " + ztsIP + ":9090 "
    commandList = []
    if neType == "sdl":
        command1 = commonStr + "-realm sdl_default_realm -p " + umpassword + " -g " + path  + "sdlcnf_default_groups.json"
        command2 = commonStr + " -realm sdl_default_realm -p " + umpassword + " -u " + path  + "sdlcnf_default_users.json"
        command3 = commonStr + "-realm sdl_db_realm -p " + umpassword + " -g " + path  + "sdlcnf_default_dbgroups.json"
        command4 = commonStr + " -realm sdl_db_realm -p " + umpassword + " -u " + path  + "sdlcnf_default_dbusers.json"
        command5 = commonStr + " -realm sdl_db_realm -p " + umpassword + " -u " + path  + "sdlcnf_hssuser.json"
        commandList = [command1, command2, command3, command4, command5]
    else:
        command6 = commonStr + " -realm pgw_default_realm -p " + umpassword + " -g " + path  + "pgwcnf_default_groups.json"
        command7 = commonStr + " -realm pgw_default_realm -p " + umpassword + " -u " + path  + "pgwcnf_default_users_withoutli.json"
        command8 = commonStr + "-realm pgw_default_realm -p " + umpassword + " -u " + path  + "pgwcnf_default_users_withli.json"
        commandList = [command6, command7, command8]
    for command in commandList:
        print("command is" + command)
        p1 = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        output, err = p1.communicate()
        err = err.decode()
        output = output.decode()
        print("output:" + output + " err: " + err)
        if "successfully" not in str(output.strip()):
            print("command:" + command + " , run failed with error:" + err)
            sys.exit(1)
        if "duplicate" in str(output.strip()):
            print("command partial successfully as " + output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', required=True, help="ZTS envoylb IP")
    parser.add_argument('-d', '--directory', required=True, help="Package directory")
    parser.add_argument('-p', '--adminpasswd', required=True, help="Password of ZTS admin user")
    parser.add_argument('-w', '--hsspasswd', default="siemens", help="Password of HSS user")
    parser.add_argument('-n', '--netype', help="netype, like sdl or pgw")

    args = parser.parse_args()
    ztsIP = args.ip
    packagedir = args.directory
    ztsPasswd = args.adminpasswd
    hssPasswd = args.hsspasswd
    neType = args.netype
    packagedir = packagedir + "/zts_um/"
    updateUserFiles(packagedir, hssPasswd, neType)
    createRealm(packagedir, ztsIP, ztsPasswd, neType)
    provisionUM(packagedir, ztsIP, ztsPasswd, neType)
    print('Finish run script provisionUsersAndGroups.py.')
    sys.exit(0)
