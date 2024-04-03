#!/bin/bash

set -x

#source post_pgw.cfg

CONTROL_IP="${1}"
CONTROL_USER="${2}"
CONTROL_PWD="${3}"

SDL_NAMESPACE="${4}"
DIAG_POD_PREFIX="${5}"

SDL_CITM_EXT_OAM_IP="${6}"
SDL_NETCONF_USER="${7}"
SDL_NETCONF_PWD="${8}"

EXPS_TO_BE_INSTALLED_PATH="${9}"
EXPS_SEQUENCE="${10}"
OPERATE_LIST="${11}"

#EXPS_TO_BE_INSTALLED_PATH="exps_to_be_installed"
#EXPS_SEQUENCE="COMMON PGW 3GPPHSS HLR HSSIMS HSSEPS UDM5G LI3GPPHSS"
#OPERATE_LIST="load-exp prepare-exp activate-exp"

which sshpass
if [ $? != 0  ]; then
    echo "Please install the sshpass!"
    exit 1
fi

sshpass -p ${CONTROL_PWD} ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${CONTROL_USER}@${CONTROL_IP} "rm -rf /tmp/exps_to_be_installed"
sshpass -p ${CONTROL_PWD} ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${CONTROL_USER}@${CONTROL_IP} "mkdir -p /tmp/exps_to_be_installed"
sshpass -p ${CONTROL_PWD} scp -r -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${EXPS_TO_BE_INSTALLED_PATH}/*  ${CONTROL_USER}@${CONTROL_IP}:/tmp/exps_to_be_installed

DIAG_POD_NAME=`sshpass -p ${CONTROL_PWD} ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${CONTROL_USER}@${CONTROL_IP} "kubectl get pod -n ${SDL_NAMESPACE} |grep ${DIAG_POD_PREFIX}|head -1"|cut -d' ' -f1`

for exp in `find ${EXPS_TO_BE_INSTALLED_PATH}/*.tar|awk -F '/' '{print $NF}'`; do
    echo "${exp}"
    sshpass -p ${CONTROL_PWD} ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${CONTROL_USER}@${CONTROL_IP} "kubectl cp /tmp/exps_to_be_installed/${exp} ${DIAG_POD_NAME}:/var/SharedStorage/exps/stage/ -n ${SDL_NAMESPACE}"
done

sleep 1m

for exp in ${EXPS_SEQUENCE}; do
    echo "${exp}"

    if ls ${EXPS_TO_BE_INSTALLED_PATH}|grep "\-"$exp; then
        ver=`ls ${EXPS_TO_BE_INSTALLED_PATH}|grep "\-"$exp|cut -d'-' -f3,4`

        for opt in ${OPERATE_LIST}; do
            echo "Start to ${opt} ${exp}-${ver}."
            cp curl_exp.tpl curl_exp.tmp
            sed -i -e 's/CMD/'${opt}'/g' -e 's/NAME/'${exp}'/g' -e 's/VERSION/'${ver}'/g' -e 's/CONFDVIP/'${SDL_CITM_EXT_OAM_IP}'/g' -e 's/USER/'${SDL_NETCONF_USER}'/g' -e 's/PWD/'${SDL_NETCONF_PWD}'/g' curl_exp.tmp
            mkdir -p logs
            bash curl_exp.tmp > logs/curl-${exp}-${opt}.log
            sleep 10
            tid=`cat logs/curl-${exp}-${opt}.log|grep transaction-id|cut -d'"' -f4`
            res="JOBS_IN_EXECUTION"
            while [ "$res" == "JOBS_IN_EXECUTION" ]; do
                sleep 10
                curl -k -X GET -u ${SDL_NETCONF_USER}:${SDL_NETCONF_PWD} -H "Accept:application/vnd.yang.data+json" https://${SDL_CITM_EXT_OAM_IP}:28809/api/operational/sdl/state/derived-state/deployments/deployment/1/vnf-instances/vnf-instance/A/operation/transactions/transaction/${tid}?deep > logs/jobs-${exp}-${opt}-${tid}.log
                res=`grep status logs/jobs-${exp}-${opt}-exp-${tid}.log |head -n 1|cut -d'"' -f4`
            done ### END while ###
            if [ "$res" == "SUCCESS" ]; then
                echo "${opt} ${exp}-${ver} success."
                sleep 15
            else
                echo "${opt} ${exp}-${ver} fail."
                exit 1
            fi
        done ### END for opt ###

    else
        echo "${exp} package not found!"
        exit 1
    fi ### END if ls exp ###

done ### END for exp ###


curl -k -X GET -u "${SDL_NETCONF_USER}:${SDL_NETCONF_PWD}" -H "Accept:application/vnd.yang.data+json" https://${SDL_CITM_EXT_OAM_IP}:28809/api/operational/sdl/state/derived-state/deployments/deployment/1/vnf-instances/vnf-instance/A/extensions?deep | grep -i -B 2 \"activated\"

