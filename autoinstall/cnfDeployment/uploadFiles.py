#!/usr/bin/python3

import os
import sys
import datetime
import time
import hashlib
from optparse import OptionParser  
import subprocess

ztsuser = "zts1user"
ztspasswd = "User@1234"
dummyVnfid = ""
ztsenvoylbip = ""
netconffile = ""
secrettarfile = ""
caclientcli = ""
vnfid = ""

def usageMsg():
    msg = "Usage: python uploadFiles.py -v [VNFID] -p [Password Of zts1user] -z [ZTSEnvoylbIP] -c [caclientcli] -n [NetconfFile] -s [SecretTarFile]\n"
    msg += "For example:\n python uploadFiles.py -v qdlab1 -p User@1234 -z 10.67.35.34 -c /root/caclientcli -n /root/qdlab1.xml -s /root/secret-provision.tar \n"
    return msg

def generatevnfid():
    global dummyVnfid
    sha256 = hashlib.sha256()
    sha256.update(str(int(time.time())).encode('utf-8'))
    dummyVnfid = "nreg" + sha256.hexdigest()[0:10]

def cmd_exec(cmd):
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    pdu_data, stderr_pdu = proc.communicate(
        ('through stdin to stdout').encode())
    data = pdu_data.decode()
    err = stderr_pdu.decode()
    return data, err, proc.returncode

def uploadhandle():
    cmd = "curl --connect-timeout 120 --max-time 480 --retry 5 --retry-delay 10 --retry-max-time 480 -k -X GET -F user=zts1user -F passwd=" + ztspasswd + " -F vnfid=" + dummyVnfid + " https://" + ztsenvoylbip+ ":8175/fetchvnfkey"
    print("cmd: ", cmd)
    d, e, __ = cmd_exec(cmd)
    if "dplicated" in (e).strip() or "disconnected" in (e).strip():
        print((e).strip())
        sys.exit(-1)
    vnfpasswd = (d).strip()

    certsdir = "/tmp/" + dummyVnfid
    if not os.path.exists(certsdir):
        os.system('mkdir -p ' + certsdir )

    cmd = "openssl genrsa -out " + certsdir + "/key.pem 2048"
    os.system(cmd)

    cmd = caclientcli + " --secure getCert --server " + ztsenvoylbip + ":9096 --user " + dummyVnfid + " --pass " + vnfpasswd + " --sub /CN=nokia.com/O=nokia/C=IN --key " + certsdir + "/key.pem --out "+ certsdir
    os.system('chmod 777 ' + caclientcli)
    print("cmd", cmd)
    d, e, resultcode = cmd_exec(cmd)
    if 0 != resultcode:
        print((e).strip())
        sys.exit(-1)

    cmd = "openssl x509 -inform der -in " + certsdir + "/cacert.der -out " + certsdir + "/cacert.pem"
    print("cmd: ", cmd)
    os.system(cmd)

    cmd = "openssl x509 -inform der -in " + certsdir + "/cert.der -out " + certsdir + "/cert.pem"
    print("cmd: ", cmd)
    os.system(cmd)

    cmd = 'curl --cacert ' + certsdir + '/cacert.pem --key ' + certsdir + '/key.pem --cert ' + certsdir + '/cert.pem -X POST -F vnfid="' + vnfid +  '" -F uploadfile=@' + netconffile + ' https://' + ztsenvoylbip + ':8075/uploadxml'
    print("cmd: ", cmd)
    d, e, __ = cmd_exec(cmd)
    if "fail" in (e).strip() or "fail" in (d).strip():
        print((e).strip())
        sys.exit(-1)
    print((d).strip())

    cmd = 'curl --cacert ' + certsdir + '/cacert.pem --key ' + certsdir + '/key.pem --cert ' + certsdir + '/cert.pem -X POST -F vnfid="' + vnfid +  '" -F uploadfile=@' + secrettarfile + ' https://' + ztsenvoylbip + ':8075/uploadjson'
    print("cmd: ", cmd)
    d, e, __ = cmd_exec(cmd)
    if "fail" in (e).strip() or "fail" in (d).strip():
        print((e).strip())
        sys.exit(-1)
    print((d).strip())
    os.system("rm -rf " + certsdir)

def checkInputFiles():
    if not os.path.exists(netconffile):
        print(netconffile + " file1 is not exist.")
        sys.exit(-1)
    if not os.path.exists(secrettarfile):
        print(secrettarfile + "  file2 is not exist.")
        sys.exit(-1)
    if not os.path.exists(caclientcli):
        print(caclientcli + " file 3 is not exist")

if "__main__" == __name__:
    parser = OptionParser(usageMsg())  
    parser.add_option("-v", "--vnfid", dest="vnfid", help="vnfid")
    parser.add_option("-p", "--passwd", dest="ztspasswd", help="Password of zts1user")
    parser.add_option("-z", "--ztsenvoylbip", dest="ztsenvoylbip", help="External IP of ZTS ENVOY LB POD.")
    parser.add_option("-c", "--caclientcli", dest="caclientcli", help="The path of caclientcli")
    parser.add_option("-n", "--netconffile", dest="netconffile", help="The netconf xml will be uploaded.")
    parser.add_option("-s", "--secrettarfile", dest="secrettarfile", help="The secret tar will be uploaded.")
    (options, args) = parser.parse_args()
    if not options.vnfid or not options.ztsenvoylbip or not options.ztspasswd or not options.netconffile or not options.secrettarfile or not options.caclientcli:
        parser.error("incorrect number of arguments")
    ztsenvoylbip = options.ztsenvoylbip
    ztspasswd = options.ztspasswd
    netconffile = options.netconffile
    secrettarfile = options.secrettarfile
    caclientcli = options.caclientcli
    vnfid = options.vnfid

#check the input and process
    checkInputFiles()
    generatevnfid()
    uploadhandle()
    sys.exit(0)

