#!/bin/bash

set -x


sshpass -p ${testclient_pwd} scp -r -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null provisionOperation.sh ${testclient_user}@${testclient_ip}:${aep_package_path_lpc}

sshpass -p ${testclient_pwd} scp -r -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null netconf-console ${testclient_user}@${testclient_ip}:${aep_package_path_lpc}


sshpass -p ${testclient_pwd} ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${testclient_user}@${testclient_ip} "${aep_package_path_lpc}/provisionOperation.sh ${aep_package_path_lpc} ${exps_sequence} ${pgwops_user} ${pgwops_pwd} ${pgwops} ${pgw_pwd} ${pgw}" 


