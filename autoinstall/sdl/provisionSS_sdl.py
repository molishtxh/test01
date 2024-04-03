#!/usr/bin/python

import os
import pexpect
import sys
import json
import random
from collections import OrderedDict
sys.path.append("../sdl")
import common


def get_json_data_mn(sourceType):
    with open('./MANIFEST.json', 'rb') as f:
        params = json.load(f, object_pairs_hook = OrderedDict)
        params[0]['SourceType'] = sourceType
        print("params:",params)
    return params

def write_json_data_mn(params):
    with open('./MANIFEST.json', 'w') as r:
        json.dump(params, r, sort_keys=False, indent=4, separators=(',', ': '))

def update_manifest(sourceType):
    #sourceType = 'SDL'
    the_revised_dict = get_json_data_mn(sourceType)
    write_json_data_mn(the_revised_dict)

def get_update_list(update_ss_file):
    key_values = dict()
    NeType = ""
    jsonfile = ""
    applicationName = ""
    if not os.path.exists(update_ss_file):
        print(("Error: file " + update_ss_file + " not exist"))
        sys.exit(-1)
    lines = open(update_ss_file, 'r')
    for line in lines:
        line = line.strip().split('::')
        if line[0] != "NeType" and line[0] != "vnfId" and line[0] != "jsonfile" and line[0] != "applicationName":
            key_values[line[0]] = line[1]
        elif line[0] == "NeType":
            NeType = line[1]
        elif line[0] == "jsonfile":
            jsonfile = line[1]
        elif line[0] == "applicationName":
            applicationName = line[1]

    lines.close()
    if not os.path.exists(jsonfile):
        print(("Error: file " + jsonfile + " not exist"))
        sys.exit(-1)
    print(jsonfile, applicationName, NeType)
    return (key_values, jsonfile, applicationName, NeType)

def get_json_data(update_ss_file, sdl_vnfid):
    (key_values, jsonfile, applicationName, NeType) = get_update_list(update_ss_file)
    with open(jsonfile, 'rb') as f:
        params = json.load(f, object_pairs_hook = OrderedDict)
        params['vaultsecrets']['NeType'] = NeType
        params['vaultsecrets']['VNFs'][0]['vnfId'] = sdl_vnfid
        for item in params['vaultsecrets']['VNFs']:
            for item2 in item['CustomerRelVersion']:
                applicationName_list = []
                for item3 in item2['applications']:
                    applicationName_list.append(item3['applicationName'])
                    name_list = []
                    if item3['applicationName'] == applicationName:
                        for item4 in item3['secret']:
                            name_list.append(item4['name'])
                            for key in key_values:
                                if item4['name'] == key:
                                    item4['value'] = key_values[key]
                        print(name_list)
                        for key in key_values:
                            if key not in name_list:
                                print("Append the new secret!!")
                                tmpSecret = OrderedDict()
                                tmpSecret2 = OrderedDict()
                                tmpSecret['name'] = key
                                tmpSecret['Type'] = "text"
                                tmpSecret['oper'] = "WRITE"
                                tmpSecret['holder'] = ""
                                tmpSecret['value'] = key_values[key]
                                tmpSecret2['expiry'] = "no"
                                tmpSecret['expiration'] = tmpSecret2
                                item3['secret'].append(tmpSecret)
                print("The applicationName list is: ")
                print(applicationName_list)
                if applicationName not in applicationName_list:
                    print("Did not find the applicationName: " + applicationName)
                    tmpAppName = OrderedDict()
                    tmpAppName['applicationName'] = applicationName
                    print(tmpAppName)
                    secret_list = []
                    for key in key_values:
                        print("Append the new secret: " + key)
                        tmpSecret = OrderedDict()
                        tmpSecret2 = OrderedDict()
                        tmpSecret['name'] = key
                        tmpSecret['Type'] = "text"
                        tmpSecret['oper'] = "WRITE"
                        tmpSecret['holder'] = ""
                        tmpSecret['value'] = key_values[key]
                        tmpSecret2['expiry'] = "no"
                        tmpSecret['expiration'] = tmpSecret2
                        print(tmpSecret)
                        secret_list.append(tmpSecret)
                    tmpAppName['secret'] = secret_list
                    item2['applications'].append(tmpAppName)
    return (jsonfile, params)

def write_json_data(jsonfile, params):
    with open(jsonfile, 'w') as r:
        json.dump(params, r, sort_keys=False, indent=2, separators=(',', ': '))

def update_secret_sdl(upd_sdl_ss, sdl_vnfid):
    #note: the data file need to be updated for secret_sdl.json
    #upd_sdl_ss = './upd_sdl_ss.txt'
    (updated_sdl_jsonfile, the_revised_sdl_dict) = get_json_data(upd_sdl_ss, sdl_vnfid)
    write_json_data(updated_sdl_jsonfile, the_revised_sdl_dict)

def transferSS(cert_path, sdl_metadata_path, zts_ns):
    metadata_files = ['MANIFEST.json', 'diag', 'diag.pub', 'ops', 'ops.pub', 'sdl', 'sdl.pub', 'ss_sdl_metadata.tar', 'SS/secret_sdl.json']
    cert_files = ['cacert.der','cacert.pem', 'cert.der', 'cert.pem', 'certs.tar', 'key.pem']
    for file in metadata_files:
        cmd = 'kubectl cp ' + sdl_metadata_path + '/' + file + ' vaultagent-0:/tmp/ -n ' +zts_ns
        print(cmd)
        os.system(cmd)
        os.system('rm ' + sdl_metadata_path + '/' + file)
    for file in cert_files:
        cmd = 'kubectl cp ' + cert_path + '/' + file + ' vaultagent-0:/tmp/ -n ' +zts_ns
        print(cmd)
        os.system(cmd)
        os.system('rm ' + cert_path + '/' + file)

def uploadSS(secretFile, ssuser, ssuser_pwd, zts_ns):
    #example usage:
    #uploadSS('/tmp/secret_sdl.json', 'zts1user', 'User@1234')
    #secretFile = '/tmp/secret_sdl.json'
    #ssuser = 'zts1user'
    #ssuser_pwd = 'User@1234'
    child = pexpect.spawn('kubectl exec -it vaultagent-0 -n ' + zts_ns + ' -- sscli batchUpload --file ' + secretFile)
    #child = pexpect.spawn('kubectl exec -it vaultagent-0 -n ' + zts_ns + ' -- sscli listSec --VnfId sdlcet --RelVer 1 --AppId sdlsecrets --NeType SDL')
    ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'Please Enter UserName:*'],timeout=60)
    if ret != 2:
        print("Error during run sscli batchUpload command.")
        child.sendline("exit\r")
        sys.exit(-1)
    child.sendline(ssuser)
    ret = child.expect([pexpect.TIMEOUT,pexpect.EOF,'Please Enter Password:*'],timeout=120)
    if ret != 2:
        print("No expected Password during run sscli batchUpload command.")
        child.sendline("exit\r")
        sys.exit(-1)
    child.sendline(ssuser_pwd+'\n')
    print(child.read())
    ret = child.expect([pexpect.EOF,pexpect.TIMEOUT,'(?i)are successfully written(?i)', '(?i)Access token verification failed(?i)'], timeout=120)
    if ret == 0:
        print("Secrets " + secretFile + " is successfully written.\n")
    else:
        print("Secrets " + secretFile + " is failed written.\n")
    child.sendline("exit\r")

def prepareAllSecrets(cert_path, zts_envoylb_ip, zts1user, zts1_pwd, ss_src_pkg_path, sdl_metadata_path, ss_config_file, secret_sdl_file, sdl_vnfid, zts_ns = "zts-default"):
    #example: cert_path = '/certs', sdl_ip = '10.93.98.129', zts1user = 'zts1user', zts1_pwd = 'User@1234'
    #         ss_src_pkg_path = '/root/jiangjil/SDL_2250.0.2030/INSTALL_MEDIA/MISC/zts_ss'
    #         sdl_metadata_path = '/opt/sdl/metadata'
    #         ss_config_file = '/root/aupan/upd_sdl_ss.txt'
    if not os.path.exists(cert_path):
        os.makedirs(cert_path)
    os.chdir(cert_path)
    cmd = 'openssl genrsa -out ' + cert_path + '/ztskey.pem 2048'
    print(cmd)
    os.system(cmd)
    if len(sdl_vnfid) <=0:
        print("The provisioned vnfid is null")
        return
    vnfid_r = sdl_vnfid + str(random.randint(0,100000))
    cmd = 'curl --connect-timeout 120 --max-time 480 --retry 5 --retry-delay 10 --retry-max-time 480 -k -X GET -F user=' + zts1user +' -F passwd=' + zts1_pwd +' -F vnfid=' + vnfid_r +' https://' + zts_envoylb_ip + ':8175/fetchvnfkey'
    print(cmd)
    secret_str = os.popen(cmd).read() #secret_str = 'yaVzrFktjg'
    print("the return result is: " + secret_str)
    cmd = 'curl -k -X GET --user ' + vnfid_r +':' + secret_str +' https://' + zts_envoylb_ip + ':9095/caproxy/certificates -F subjAltName=\"\" -F subj=\"/CN=nokia.com/O=nokia/C=IN\" -F expDate=\"\" -F keyfile=\"@' + cert_path + '/ztskey.pem\" --output ' + cert_path + '/certs.tar'
    print(cmd)
    os.system(cmd)
    if not os.path.exists(cert_path + '/certs.tar') or not os.path.exists(cert_path + '/ztskey.pem'):
        print("certs.tar or ztskey.pem does not exist")
        return
    cmd = 'tar -xvf ' + cert_path + '/certs.tar'
    print(cmd)
    os.system(cmd)
    if not os.path.exists(cert_path + '/cacert.der') or not os.path.exists(cert_path + '/cert.der'):
        print("cacert.der or cert.der does not exist")
        return
    cmd = 'openssl x509 -inform der -in /certs/cacert.der -out ' + cert_path + '/cacert.pem'
    print(cmd)
    os.system(cmd)
    cmd = 'openssl x509 -inform der -in /certs/cert.der -out ' + cert_path + '/cert.pem'
    print(cmd)
    os.system(cmd)
    cmd = 'mv ' + cert_path + '/ztskey.pem ' + cert_path + '/key.pem'
    print(cmd)
    os.system(cmd)
    ###############################
    os.chdir(ss_src_pkg_path)
    if not os.path.exists(ss_src_pkg_path + '/ss_sdl_metadata.tar'):
        print("ss_sdl_metadata.tar does not exist")
        return
    if not os.path.exists(sdl_metadata_path):
        os.makedirs(sdl_metadata_path)
    cmd = 'cp ' + ss_src_pkg_path + '/ss_sdl_metadata.tar ' + sdl_metadata_path + '/ss_metadata.tar'
    print(cmd)
    os.system(cmd)
    ################################
    os.chdir(sdl_metadata_path)
    cmd = 'ssh-keygen -t rsa -f sdl -P \"\"'
    print(cmd)
    os.system(cmd)
    cmd = 'ssh-keygen -t rsa -f diag -P \"\"'
    print(cmd)
    os.system(cmd)
    cmd = 'ssh-keygen -t rsa -f ops -P \"\"'
    print(cmd)
    os.system(cmd)
    cmd = 'tar -xvf ss_metadata.tar'
    print(cmd)
    os.system(cmd)
    if not os.path.exists(sdl_metadata_path + '/MANIFEST.json') or not os.path.exists(sdl_metadata_path + '/SS/secret_sdl.json'):
        print("MANIFEST.json or SS/secret_sdl.json does not exist")
        return
    # cover secret_sdl.json with template
    cmd = 'cp ' + secret_sdl_file + ' ' + sdl_metadata_path + '/SS/secret_sdl.json'
    print(cmd)
    os.system(cmd)
    update_manifest('SDL')
    update_secret_sdl(ss_config_file, sdl_vnfid)
    cmd = 'tar -cvf ss_sdl_metadata.tar MANIFEST.json SS/'
    print(cmd)
    os.system(cmd)
    (key_values, jsonfile, applicationName, NeType) = get_update_list(ss_config_file)
    cmd = 'curl --cacert ' + cert_path + '/cacert.pem --key ' + cert_path + '/key.pem --cert ' + cert_path + '/cert.pem -F Address=\"127.0.0.1:8888\" -F Upload=true -F vnfid=\"' + sdl_vnfid + '\" -F uploadfile=@' + sdl_metadata_path + '/ss_sdl_metadata.tar https://' + zts_envoylb_ip + ':8075/uploadmetadata'
    print(cmd)
    os.system(cmd)
    #copy secrets to vaultagent
    transferSS(cert_path, sdl_metadata_path, zts_ns)
    uploadSS('/tmp/secret_sdl.json', zts1user, zts1_pwd, zts_ns)

#example to use these functions:
cert_path = '/certs'
zts1user = 'zts1user'
sdl_metadata_path = '/opt/sdl/metadata'
ss_config_file = os.getcwd() + '/' + 'upd_sdl_ss.txt'
secret_sdl_file = os.getcwd() + '/' + 'secret_sdl.json'
configureMap = common.parseGlobalValues('../sdl/sdl_values.yaml')
sdl_ip = configureMap['sdl_ip']
print("sdl_ip is: " + sdl_ip)
zts_envoylb_ip = configureMap['zts_envoylb_ip1']
print("zts_envoylb_ip1 is: " + zts_envoylb_ip)
zts_ns = configureMap['zts_ns']
print("zts_ns is: " + zts_ns)
zts1user_sercet = configureMap['zts1user_sercet']
print("zts1user_sercet is: " + zts1user_sercet)
sdl_ss_pkg_path = configureMap['sdl_ss_pkg_path']
print("sdl_ss_pkg_path is: " + sdl_ss_pkg_path)
sdl_vnfid_g = configureMap['sdl_vnfid']
print("sdl_vnfid_g is: " + sdl_vnfid_g)
prepareAllSecrets(cert_path, zts_envoylb_ip, zts1user, zts1user_sercet, sdl_ss_pkg_path, sdl_metadata_path, ss_config_file, secret_sdl_file, sdl_vnfid_g, zts_ns)

