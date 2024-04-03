#!/bin/bash

scriptHome=$(cd "$(dirname "$0")";pwd)
source $scriptHome/${1}

# create bcmt-admin container

containerName=bcmt-admin-$VNFID
# In NCS22, podman replaces docker
containerCommand=$(which podman &>/dev/null && echo podman || echo docker)
additionalVolume=$(which podman &>/dev/null && echo "" || echo "-v /var/run/docker.sock:/var/run/docker.sock -v /etc/docker/certs.d:/etc/docker/certs.d")

bcmtAdmin=$(${containerCommand} ps | grep "$containerName")
if [[ $bcmtAdmin == "" ]]; then
	bcmtAdminRepo=$(${containerCommand} images | grep -i bcmt-admin | awk -F " " '{print $1}')
	echo " bcmt admin repo is $bcmtAdminRepo"
	bcmtAdminVer=$(${containerCommand} images | grep -i bcmt-admin | awk -F " " '{print $2}' | awk 'NR==1')
	echo " bcmt admin version is $bcmtAdminVer"
    ${containerCommand} run -dit --restart=always --name=$containerName --net=host --privileged=true -v /opt/bcmt:/opt/bcmt $additionalVolume $bcmtAdminRepo:$bcmtAdminVer deployment
fi

echo "bcmt admin container is $containerName"
