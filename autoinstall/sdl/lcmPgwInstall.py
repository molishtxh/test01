#!/usr/bin/python3

import os
import sys
import re
import datetime
import time
from optparse import OptionParser
import logging
import subprocess
import common

#specfic product
import lcmCommon

configureMap = {}
scriptHome = os.path.dirname(sys.argv[0])
pythonPath = "/usr/bin/python3 "

scriptHome = "."
if os.path.dirname(sys.argv[0]) != "":
    scriptHome = os.path.dirname(sys.argv[0]) + "/"
scriptHome = scriptHome + "/"

def untar_package(enable):
    if "enable" == enable:
        msg = "unTar package failed with error: "
        if os.path.exists("sdl_values.yaml"):
            cmd = pythonPath + " cnfsdl.py -m untar_package -s sdl_values.yaml"
            lcmCommon.cmd_exec(cmd, msg)
        else:
            lcmCommon.logger.info("sdl_values.yaml not exists, skip sdl config")
        if os.path.exists("pgw_values.yaml"):
            cmd = pythonPath + " cnfsdl.py -m untar_package -p pgw_values.yaml"
            lcmCommon.cmd_exec(cmd, msg)
        else:
            lcmCommon.logger.info("pgw_values.yaml not exists, skip pgw config")
    else:
        lcmCommon.logger.info("skip untar package")

def prepare_helm_values():
    lcmCommon.logger.info("============generate value.yaml========")
    msg = "values.yaml generation failed with error: "
    if os.path.exists("sdl_values.yaml"):
        cmd = pythonPath + " cnfsdl.py -m prepare_helm_values -s sdl_values.yaml"
        lcmCommon.cmd_exec(cmd, msg)
    else:
        lcmCommon.logger.info("sdl_values.yaml not exists, skip sdl config")
    if os.path.exists("pgw_values.yaml"):
        cmd = pythonPath + " cnfsdl.py -m prepare_helm_values -p pgw_values.yaml"
        lcmCommon.cmd_exec(cmd, msg)
    else:
        lcmCommon.logger.info("pgw_values.yaml not exists, skip pgw config")

def generate_um(neType="pgw"):
    lcmCommon.logger.info("============generate um and groups========")
    cmd = ""
    if neType == "sdl":
        cmd = pythonPath + " provisionUsersAndGroups.py -i " + ztsEnvoylbIP +  " -d " + sdl_package_path + "/INSTALL_MEDIA/MISC/ -p " + zts_admin_passwd +  " -w siemens -n sdl"
    else:
        cmd = pythonPath + " provisionUsersAndGroups.py -i " + ztsEnvoylbIP +  " -d " + pgw_package_path + "/INSTALL_MEDIA/MISC/ -p " + zts_admin_passwd +  " -w siemens -n pgw"
    msg = "Finish run script provisionUsersAndGroups.py"
    lcmCommon.cmd_exec(cmd,msg)

def prepare_all():
    lcmCommon.logger.info("============prepare all start========")
    untar_package("enable")
    prepare_helm_values()
    generate_um()
    provisionSS_pgw()

def onboard_images_charts():
    cmd="sh " + scriptHome + "ncm_onboarding_script.sh " +str(ncm_admin_user)+" "+str(ncm_admin_pwd)+" "+str(control_ip)+" "+str(bcmt_port)+" "+str(pgw_package_path)
    os.system(cmd)

def deploy_only():
    lcmCommon.logger.info("============deploy_only start========")
    labInstall()
    install_exps()
    aep_provision()

def labInstall():
    lcmCommon.logger.info("============labInstall========")
    cmd="sh " + scriptHome + "bringUpSdl.sh " +str(sdl_ns)+" "+str(pgw_ns)+" "+str(sdl_install_path)+" "+str(pgw_install_path)+" "+str(sdl_crd_path)+" "+str(pgw_crd_path)+" "+"pgw"
    os.system(cmd)

def cleanup_image_charts():
    lcmCommon.logger.info("============cleanup_images========")
    cmd="cd " + scriptHome; "sh cleanUpImage.sh " +ncm_admin_user+" "+ncm_admin_pwd+" "+control_ip+" "+bcmt_port+" "+sdl_tag+ " "+pgw_tag
    msg = "CleanupImg failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def terminate():
    labUnInstall()
    cleanup_image_charts()

def labUnInstall():
    cmd="sh " + scriptHome + "deleteSdl.sh " +str(sdl_ns)+" "+str(pgw_ns)+" "+str(sdl_install_path)+" "+str(pgw_install_path)+" "+str(sdl_crd_path)+" "+str(pgw_crd_path)+" "+"pgw"
    os.system(cmd)

def install_exps():
    lcmCommon.logger.info("============install_exps========")
    cmd = pythonPath + " installExps.py "
    msg = "install exps failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def aep_provision():
    lcmCommon.logger.info("============aep_provision========")
    #cmd =  "./aepProvision.sh "
    cmd = pythonPath + " aepProvision.py "
    msg = "aep provision failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def provisionSS_pgw():
    lcmCommon.logger.info("============provisionSS_pgw========")
    cmd = pythonPath + " ./provisionSS_pgw.py "
    msg = "provisionSS_pgw failed with error: "
    lcmCommon.cmd_exec(cmd, msg)

def deploy():
    lcmCommon.logger.info("============deploy start===========")
    prepare_all()
    onboard_images_charts()
    deploy_only()

class pgwInstall(lcmCommon.installCnfProduct):
    def deployEntry(self):
        lcmCommon.logger.info("============deploy start===========")
        init()
        prepare_all()
        onboard_images_charts()
        deploy_only()
    def preHealthcheckEntry(self):
        lcmCommon.logger.info("============to do===========")
    def prepareEntry(self):
        lcmCommon.logger.info("============prepare start===========")
        init()
        prepare_all()
    def deployOnlyEntry(self):
        lcmCommon.logger.info("============deploy only start===========")
        init()
        deploy_only()
    def postHealthcheckEntry(self):
        lcmCommon.logger.info("============to do===========")
    def terminateEntry(self):
        lcmCommon.logger.info("============terminate start===========")
        init()
        terminate()


def init():
    global sdl_vnfid
    global pgw_vnfid
    global sdl_install_path
    global pgw_install_path
    global sdl_crd_path
    global pgw_crd_path
    global ncm_admin_user
    global ncm_admin_pwd
    global control_ip
    global bcmt_port
    global sdl_package_path
    global pgw_package_path
    global sdl_tag
    global pgw_tag
    global zts_admin_passwd
    global ztsEnvoylbIP

    configureMap = common.parseGlobalValues('./sdl_values.yaml')
    sdl_vnfid = configureMap['sdl_vnfid']
    pgw_vnfid = configureMap['pgw_vnfid']
    sdl_ns = configureMap['sdl_ns']
    pgw_ns = configureMap['pgw_ns']
    sdl_install_path = configureMap['sdl_install_path']
    pgw_install_path = configureMap['pgw_install_path']
    sdl_crd_path = configureMap['sdl_crd_path']
    pgw_crd_path = configureMap['pgw_crd_path']
    ncm_admin_user = configureMap['ncm_admin_user']
    ncm_admin_pwd = configureMap['ncm_admin_pwd']
    control_ip = configureMap['control_ip']
    ztsEnvoylbIP = configureMap['zts_envoy_ip1']
    bcmt_port = configureMap['bcmt_port']
    sdl_package_path = configureMap['sdl_package_path']
    pgw_package_path = configureMap['pgw_package_path']
    sdl_tag = configureMap['sdl_tag']
    pgw_tag = configureMap['pgw_tag']
    zts_admin_passwd = configureMap['zts_admin_passwd']
