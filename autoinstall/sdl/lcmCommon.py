#!/usr/bin/python3

import os
import sys
import re
import datetime
import time
from optparse import OptionGroup, OptionParser
from abc import abstractmethod, ABCMeta
import logging
import subprocess
import common


lcmProducts=['HSS', 'SDL', 'PGW']

lcmOptions={\
"deploy":"                       End to End installation process ",\
"pre_healthcheck":"              Check before installation  ",\
"prepare":"                      Prepare package or yaml files  ",\
"deploy_only":"                  Lab installation.",\
"post_healthcheck":"              Check after installation  ",\
"terminate":"                    Lab termination  "}

logger = logging.getLogger(__name__)

class installCnfProduct(metaclass=ABCMeta):
    #abstractMethod
    def deploy(self):
        pass
    def pre_healthcheck(self):
        pass
    def prepare(self):
        pass
    def deploy_only(self):
        pass
    def post_healthcheck(self):
        pass
    def terminate(self):
        pass

def logFile():
    global logfile
    global logger
    path = os.path.basename(__file__).split(".")[0]
    path = path + "_log"
    if not os.path.exists(path):
        os.mkdir(path)
    logfile = path + "/lcm-" + time.strftime('%Y%m%d-%H-%M', time.localtime(time.time())) + ".log"
    print("The log file is " + logfile)
    logger.setLevel(level=logging.DEBUG)
    handler = logging.FileHandler(logfile, mode='w')
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.addHandler(console)

def cmd_exec(cmd, msg):
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
    resultcode = proc.returncode
    if resultcode != 0:
        logger.error(msg + (data).strip() + (err).strip())
        sys.exit(-1)
    logger.info((data).strip())