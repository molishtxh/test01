#!/bin/bash

#NREG_PKG="/elk/leo/"
#LOAD_NUM="NREG_22.0-2200297" Note: sif need to onbard targetted upgrade load, then give num in $2
#VNFID="test"
#TENANT_ENABLED="true"
#TENANT_NAME="test1"
#TENANT_ADMIN_PWD="yt_xk39B"
#CONTROL_NODEIP="10.67.35.97"
#BCMT_PORTAL_PORT="8084"

scriptHome=$(cd "$(dirname "$0")";pwd)
source $scriptHome/${1}

logPath="$scriptHome/hsslcm_log"
if [ ! -d "$logPath" ]; then
	mkdir -p $scriptHome/log
	logPath=$scriptHome/log
fi
now=$(date "+%y-%m-%d_%H-%M-%S")
logFile=$logPath/onboarding_$now.log
errFile=$logPath/onboarding_${now}_err.log

logmsg()
{
    echo -e "`date \"+%y/%m/%d %H:%M:%S\"`: $1 " >> $logFile
    echo -e "`date \"+%y/%m/%d %H:%M:%S\"`: $1 "
}

if [ -n "$2" ]
then
  logmsg "this is CNF upgrade case, will onboard target images"
  LOAD_NUM=$2
fi

bcmtDir="/opt/bcmt/$VNFID/$LOAD_NUM"
dirname="$bcmtDir/INSTALL_MEDIA/IMAGES"
chartdirname="$bcmtDir/INSTALL_MEDIA/CHARTS"

if [ -d "$dirname" ]; then
	logmsg "$dirname exists"
else
	logmsg "$dirname does not exist"
fi


if [ -d "$chartdirname" ]; then
	logmsg "$chartdirname exists"
else
	logmsg "$chartdirname does not exist"
fi


# untar images
count=`ls -1 $dirname/*tar.gz | wc -l`
if [ $count != 0 ]
then
	logmsg "Found $count number of images"
        cd $dirname/
	for file in *.tar.gz;
	do
		tar -zxvf $file;
		if [ $? -eq 0 ]; then
			logmsg "Successfully untarred the image: $file"
		else
			logmsg "Failed to untar the image: $file"
			exit
		fi
		rm  $file
	done

else
	logmsg "Images not found in $dirname"
	exit 1
fi


if [[ $TENANT_ENABLED == "false" ]]
then
	ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
	ncs user login --username=$NCM_ADMIN_USR --password=$NCM_ADMIN_PWD

	logmsg "Images onboarding is triggered to BCMT repo"
	ls -1  $dirname/*tar 2> $errFile | xargs -I %% echo  "echo \"Onboarding Image \" %% | tee -a "$logFile" ; ncs app-resource image add --image_location local --image_path %% 2>> $errFile | tee -a "$logFile" " | sh
        if [ $? -eq 0 ]
            then
	    	errfilesize=$(wc -c <$errFile)
		if [ $errfilesize -gt 0 ]
		then
                	logmsg "Failed while uploading the images to BCMT repo"
			cat $errFile >> $logFile
            		exit 1
		else
                	logmsg "Successfully uploaded the images"
		fi
            else
                	logmsg "Failed while uploading the images to BCMT repo"
            		exit 1

         fi

	ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
        ncs user login --username=$NCM_ADMIN_USR --password=$NCM_ADMIN_PWD

	logmsg "Chart Onboarding is triggered to STABLE repo"
	ls -1  $chartdirname/*.tgz 2> $errFile | xargs -I %% echo  "echo \"Onboarding chart \" %% | tee -a "$logFile" ; ncm app-resource chart add --file_name %% 2>> $errFile  | tee -a "$logFile" " | sh
        if [ $? -eq 0 ]
            then
	    	errfilesize=$(wc -c <$errFile)
		if [ $errfilesize -gt 0 ]
		then
                	logmsg "Failed while uploading the charts to STABLE repo"
			cat $errFile >> $logFile
            		exit 1
		else
                	logmsg "Successfully uploaded the charts to STABLE repo"
		fi
            else
                	logmsg "Failed while uploading the charts to STABLE repo"
            		exit 1
         fi

else
	ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
	ncs user login --username=$TENANT_NAME-admin --password=$TENANT_ADMIN_PWD
        ls $dirname/*tar
	logmsg "Images onboarding triggered to Harbour repo : tenent $TENANT_NAME"
	ls -1  $dirname/*tar 2> $errFile | xargs -I %% echo  "echo \"Onboarding image \" %% | tee -a "$logFile" ; ncs tenant-app-resource image add --tenant_name $TENANT_NAME -file_path %% 2>> $errFile | tee -a "$logFile" " | sh
        if [ $? -eq 0 ]
	then
		errfilesize=$(wc -c <$errFile)
		if [ $errfilesize -gt 0 ]
		then
                	logmsg "Failed while uploading the images to Harbor repo"
			cat $errFile >> $logFile
            		exit 1
		else
                	logmsg "Successfully uploaded the images"
		fi
	else
		logmsg "Failed while uploading the images to Harbor repo"
		exit 1

	fi

	ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
	ncs user login --username=$TENANT_NAME-admin --password=$TENANT_ADMIN_PWD

        logmsg "Chart Onboarding is triggered to HARBOR repo: tenent $TENANT_NAME"
        ls -1  $chartdirname/*.tgz 2> $errFile | xargs -I %% echo  "echo \"Onboarding chart \" %% | tee -a "$logFile" ; ncs tenant-app-resource chart add --tenant_name $TENANT_NAME --file_path %% 2>> $errFile | tee -a "$logFile" " | sh
        if [ $? -eq 0 ]
            then
                errfilesize=$(wc -c <$errFile)
                if [ $errfilesize -gt 0 ]
                then
                        logmsg "Failed while uploading the charts to HARBOR repo"
                        cat $errFile >> $logFile
                        exit 1
                else
                        logmsg "Successfully uploaded the charts to HARBOR repo"
                fi
            else
                        logmsg "Failed while uploading the charts to HARBOR repo"
                        exit 1
         fi
fi
logmsg "Onboarding is done succesfully"

# remove local images
cd $dirname;rm -rf *;
logmsg "Removed local images from $dirname"
