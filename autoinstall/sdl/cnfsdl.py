#!/usr/bin/python3

import os
import sys
import re
import datetime
import time
from optparse import OptionParser
import logging
import subprocess
import yaml
import collections
import common

lcmOptions={\
"untar_package":"        untar the package.",\
"prepare_helm_values":"          Auto generate helm values base on configure file."}

sdlValuesCfgFileName = "sdl_values.yaml"
pgwValuesCfgFileName = "pgw_values.yaml"
logfile = ""
lcmMode = "deploy"
logger = logging.getLogger(__name__)
scriptHome = os.path.dirname(sys.argv[0])
pythonPath = "/usr/bin/python3 "

scriptHome = "."
if os.path.dirname(sys.argv[0]) != "":
    scriptHome = os.path.dirname(sys.argv[0]) + "/"
scriptHome = scriptHome + "/"


def usageMsg():
    msg = "Usage: /usr/bin/python3 hsslcm.py -m [LCMMODE] -i [ConfigureFileName] -y [HelmValuesInputFile]\n\n"\
          "Commands:\n"
    for key, value in lcmOptions.items():
        msg += "  " + key + value + "\n"
    msg += "\nFor example:\n"\
           "    /usr/bin/python3 lcm.py -m prepare_helm_values -i cnfdeployment.cfg -y valuesYamlTemplate.yaml\n"\
           "    /usr/bin/python3 lcm.py -m prepare_all_without_download -i cnfdeployment.cfg -y valuesYamlTemplate.yaml\n"\
           "    /usr/bin/python3 lcm.py -m deploy_only -i cnfdeployment.cfg\n"
    return msg

def logFile():
    global logfile
    global logger
    path = os.path.basename(__file__).split(".")[0]
    path = path + "_log"
    if not os.path.exists(path):
        os.mkdir(path)
    logfile = path + "/lcm-" + lcmMode + "-" + time.strftime('%Y%m%d-%H-%M', time.localtime(time.time())) + ".log"
    print("The log file is " + logfile)
    logger.setLevel(level=logging.DEBUG)
    time_line = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
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

def download_package(enable):
    logger.info("============download the package ========")
    if "sdl" == config_type:
        config_address = sdl_package_path + sdl_loadNum + ".tar.gz"
    elif "pgw" == config_type:
        config_address = pgw_package_path + pgw_loadNum + ".tar.gz"
    else:
        raise ValueError("not a correct lab type")
    cmd = "wget " + config_address
    msg = "unTar package failed with error: "
    cmd_exec(cmd, msg)

def untar_package():
    logger.info("============untar the package ========")
    if "sdl" == config_type:
        config_path = sdl_package_path + sdl_loadNum
        package_path = sdl_package_path
    elif "pgw" == config_type:
        config_path = pgw_package_path + pgw_loadNum
        package_path = pgw_package_path
    else:
        raise ValueError("not a correct lab type")
    config_file = config_path + ".tar.gz"
    chart_path = config_path + "/INSTALL_MEDIA/CHARTS/"
    if os.path.exists(config_file):
        cmd = "tar -xzvf " + config_file + " -C " + package_path
        msg = "unTar package failed with error: "
        cmd_exec(cmd, msg)
        if os.path.exists(chart_path):
            chart_list = os.listdir(chart_path)
            for chart_file in chart_list:
                if ".tgz" in chart_file:
                    cmd = "tar -xzvf " + chart_path + chart_file + " -C " + chart_path
                    cmd_exec(cmd, msg)
            logger.info(" ===== untar %s done ====" % config_file)
    else:
        logger.info("%s not exists" % config_file)

def prepare_helm_values():
    logger.info("============generate value.yaml ========")
    if "sdl" == config_type:
        configPath = sdl_package_path + sdl_loadNum + "/INSTALL_MEDIA/"
        helmValuesCfgFileName = sdlValuesYaml
    elif "pgw" == config_type:
        configPath = pgw_package_path + pgw_loadNum + "/INSTALL_MEDIA/"
        helmValuesCfgFileName = pgwValuesYaml
    else:
        raise ValueError("not a correct lab type")
    logger.info("generate %s" % helmValuesCfgFileName)
    cmd = pythonPath + " setValues.py helm_values_fileName=" + helmValuesCfgFileName + " value_path=" + configPath
    msg = "values.yaml generation failed with error: "
    cmd_exec(cmd, msg)


def checkInput(parser, options):
    if not options.lcmMode or not (options.sfileName or options.pfileName):
        parser.error("incorrect number of arguments")
        sys.exit(2)
    if options.lcmMode not in lcmOptions.keys():
        parser.error("option mode is invalid")
        sys.exit(2)
    if options.lcmMode in ['deploy', 'prepare_all', 'prepare_helm_values', 'prepare_all_without_download'] and not (options.sfileName or options.pfileName):
        parser.error("No argument -y/--file1 for values yaml generation.")
        sys.exit(2)
    if options.sfileName and (not os.path.exists(options.sfileName)):
        print(str(options.sfileName) + " file1 is not exist.")
        sys.exit(-1)
    if options.pfileName and (not os.path.exists(options.pfileName)):
        print(str(options.pfileName) + " file1 is not exist.")
        sys.exit(-1)

if "__main__" == __name__:
    parser = OptionParser(usageMsg())
    parser.add_option("-m", "--mode", dest="lcmMode", help="CNF SDL deployment options.")
    parser.add_option("-s", "--file1", dest="sfileName", help="read sdl config data from sdl_values.yaml and config to sdl target path")
    parser.add_option("-p", "--file2", dest="pfileName", help="read pgw config data from pgw_values.yaml and config to pgw target path")
    (options, args) = parser.parse_args()
    checkInput(parser, options)
    lcmMode = options.lcmMode
    sdlValuesYaml = options.sfileName
    pgwValuesYaml = options.pfileName

    logFile()
    configureMap = {}
    if sdlValuesYaml != None:
        configureMap = common.parseGlobalValues(sdlValuesYaml)
    if pgwValuesYaml != None:
        configureMap = common.parseGlobalValues(pgwValuesYaml)
        print(configureMap)

    #common
    if 'user_password' in configureMap.keys():
        user_password = configureMap['user_password']
    if 'user_password_base64' in configureMap.keys():
        user_password_base64 = configureMap['user_password_base64']

    if sdlValuesYaml != None:
        config_type = "sdl"
    elif pgwValuesYaml != None:
        config_type = "pgw"

    # zts relavent
    if 'zts_ns' in configureMap.keys():
        zts_ns = configureMap['zts_ns']
    if 'zts1user_sercet' in configureMap.keys():
        zts1user_sercet = configureMap['zts1user_sercet']
    if 'zts_envoy_ip1' in configureMap.keys():
        zts_envoy_ip1 = configureMap['zts_envoy_ip1']
    if 'zts_envoy_ip2' in configureMap.keys():
        zts_envoy_ip2 = configureMap['zts_envoy_ip2']
    if 'ztslfs_tag' in configureMap.keys():
        ztslfs_tag = configureMap['ztslfs_tag']

    #sdl relavent
    if 'sdl_ns' in configureMap.keys():
        sdl_ns = configureMap['sdl_ns']
    if 'sdl_package_path' in configureMap.keys():
        sdl_package_path = configureMap['sdl_package_path']
    if 'sdl_loadNum' in configureMap.keys():
        sdl_loadNum = configureMap['sdl_loadNum']
    if 'sdl_persistence_config' in configureMap.keys():
        sdl_persistence_config = configureMap['sdl_persistence_config']
    if 'sdl_persistence_config' in configureMap.keys():
        sdl_persistence_config = configureMap['sdl_persistence_config']
    if 'sdl_tag' in configureMap.keys():
        sdl_tag = configureMap['sdl_tag']
    if 'sdl_dockerTag' in configureMap.keys():
        sdl_dockerTag = configureMap['sdl_dockerTag']
    if 'sdl_storageClass' in configureMap.keys():
        sdl_storageClass = configureMap['sdl_storageClass']
    if 'sdl_prefix_repository' in configureMap.keys():
        sdl_prefix_repository = configureMap['sdl_prefix_repository']
    if 'sdl_sanfqdn1' in configureMap.keys():
        sdl_sanfqdn1 = configureMap['sdl_sanfqdn1']
    if 'sdl_sanfqdn2' in configureMap.keys():
        sdl_sanfqdn2 = configureMap['sdl_sanfqdn2']
    if 'sdl_vnfid' in configureMap.keys():
        sdl_vnfid = configureMap['sdl_vnfid']

    #pgw relavent
    if 'pgw_ns' in configureMap.keys():
        pgw_ns = configureMap['pgw_ns']
    if 'pgw_package_path' in configureMap.keys():
        pgw_package_path = configureMap['pgw_package_path']
    if 'pgw_loadNum' in configureMap.keys():
        pgw_loadNum = configureMap['pgw_loadNum']
    if 'ncm_admin_user' in configureMap.keys():
        ncm_admin_user = configureMap['ncm_admin_user']
    if 'ncm_admin_pwd' in configureMap.keys():
        ncm_admin_pwd = configureMap['ncm_admin_pwd']
    if 'control_ip' in configureMap.keys():
        control_ip = configureMap['control_ip']
    if 'bcmt_port' in configureMap.keys():
        bcmt_port = configureMap['bcmt_port']

    #AEP
    if 'aep_package_path' in configureMap.keys():
        aep_package_path = configureMap['aep_package_path']

    if lcmMode == "untar_package":
        untar_package()

    if lcmMode == "prepare_helm_values":
        prepare_helm_values()
