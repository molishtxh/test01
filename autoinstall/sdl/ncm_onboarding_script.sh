#!/bin/bash

NCM_ADMIN_USR=$1
NCM_ADMIN_PWD=$2
CONTROL_IP=$3
BCMT_PORTAL_PORT=$4
PKG_PATH=$5
TENANT_ENABLED='false'

#LOAD_NUM="NREG_22.0-2200297" Note: sif need to onbard targetted upgrade load, then give num in $2
#TENANT_ENABLED="true"
#TENANT_NAME="test1"
#TENANT_ADMIN_PWD="yt_xk39B"
#CONTROL_NODEIP="10.67.35.97"
#BCMT_PORTAL_PORT="8084"
#PKG_PATH=""

# usage:
# need input PKG_PATH in cfg file or load num
# ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
# ncs user login --username=$TENANT_NAME-admin --password=$TENANT_ADMIN_PWD

scriptHome=$(cd "$(dirname "$0")";pwd)
#source $scriptHome/${1}

logPath="$scriptHome/hsslcm_log"
if [ ! -d "$logPath" ]; then
        mkdir -p $scriptHome/onboardLog
        logPath=$scriptHome/onboardLog
fi
now=$(date "+%y-%m-%d_%H-%M-%S")
logFile=$logPath/onboarding_$now.log
errFile=$logPath/onboarding_${now}_err.log

logmsg()
{
    echo -e "`date \"+%y/%m/%d %H:%M:%S\"`: $1 " >> $logFile
    echo -e "`date \"+%y/%m/%d %H:%M:%S\"`: $1 "
}

#if [ -n "$2" ]
#then
#  logmsg "this is CNF upgrade case, will onboard target images"
#  LOAD_NUM=$2
#fi

dirname="$PKG_PATH/INSTALL_MEDIA/IMAGES"
echo "$dirname"

if [ -d "$dirname" ]; then
	logmsg "$dirname exists"
else
	logmsg "$dirname does not exist"
fi

# untar images
count=`ls -1 $dirname/*tar.gz | wc -l`

if [ $count != 0 ]
then
	logmsg "Found $count number of images"
else
	logmsg "Images not found in $dirname"
	exit 1
fi

#login with ncm-admin for local repo
ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1

# onboarding images
if [[ $TENANT_ENABLED == "false"  || $TENANT_ENABLED == "" ]]
then
	ncs user login --username=$NCM_ADMIN_USR --password=$NCM_ADMIN_PWD
	logmsg "Onboarding is triggered to BCMT repo"

	while [[ $retry_count -le $retry_limit ]];
	do

	ls -1  $dirname/*tar.gz 2> $errFile | xargs -I %% echo  "echo \"Onboarding Image \" %% | tee -a "$logFile" ; ncs app-resource image add --image_location local --image_path %% 2>> $errFile | tee -a "$logFile" " | sh
        if [ $? -eq 0 ]
            then
	    	errfilesize=$(wc -c <$errFile)
		if [ $errfilesize -gt 0 ]
		then
			if [[ $retry_count -eq $retry_limit ]];
			then
                logmsg "Failed while uploading the images to BCMT repo"
				cat $errFile >> $logFile
				logmsg "Retry attempts exceeded"
            			exit 1
			else
				retry_count=$((retry_count+1))
				logmsg "Failed while uploading the images to BCMT repo"
				logmsg "Retrying image upload to Harbor repo in $seconds_in_wait seconds"
				sleep $seconds_in_wait
			fi
		else
			retry_count=$((retry_limit+1))
                	logmsg "Successfully uploaded the images"
		fi
            else
                	logmsg "Failed while uploading the images to BCMT repo"
            		exit 1

         fi
	done
else
        ncs user login --username=$TENANT_NAME-admin --password=$TENANT_ADMIN_PWD

	logmsg "Onboarding triggered to Harbour repo : tenant $1"

	while [[ $retry_count -le $retry_limit ]];
	do

	ls -1  $dirname/*tar.gz 2> $errFile | xargs -I %% echo  "echo \"Onboarding image \" %% | tee -a "$logFile" ; ncs tenant-app-resource image add --tenant_name $1 -file_path %% 2>> $errFile | tee -a "$logFile" " | sh

        if [ $? -eq 0 ]
            then
		status=$(cat $logFile | grep -o '{"task-status":"failed"}')
	    	errfilesize=$(wc -c <$errFile)
		if [ $errfilesize -gt 0 ]
		then
                	if [[ $retry_count -eq $retry_limit ]];
			then
				logmsg "Failed while uploading the images to Harbor repo"
				cat $errFile >> $logFile
				logmsg "Retry attempts exceeded"
            			exit 1
			else
				retry_count=$((retry_count+1))
				logmsg "Failed while uploading the images to Harbor repo"
				logmsg "Retrying image upload to Harbor repo in $seconds_in_wait seconds"
				sleep $seconds_in_wait
			fi
		elif [ -n "${status}" ]; then
			if [[ $retry_count -eq $retry_limit ]];
                        then
				logmsg "Failed while uploading the images to Harbor repo with status failed error"
				logmsg "Retry attempts exceeded"
                                exit 1
                        else
				retry_count=$((retry_count+1))
				logmsg "Failed while uploading the images to Harbor repo with status failed error"
				logmsg "Retrying image upload to Harbor repo in $seconds_in_wait seconds"
				sleep $seconds_in_wait
                        fi
		else
			retry_count=$((retry_limit+1))
			logmsg "Successfully uploaded the images"
		fi
            else
			logmsg "Failed while uploading the images to Harbor repo"
			exit 1

        fi

	done
fi
rm -f $dirname/*.tar
logmsg "Onboarding is done successfully and extracted images are deleted"
