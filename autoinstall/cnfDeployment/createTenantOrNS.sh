#!/bin/bash

#TENANT_NAME="test1"
#TENANT_ADMIN_PWD="yt_xk39B"
#TENANT_ENABLED="true"
#HSS_NAMESPACE="test1"
#CONTROL_NODEIP="10.67.35.97"
#BCMT_PORTAL_PORT="8084"
#NCM_ADMIN_USR="ncm-admin"
#NCM_ADMIN_PWD="yt_xk39B_B"

scriptHome=$(cd "$(dirname "$0")";pwd)
source $scriptHome/cnfdeployment.cfg

#login with ncm-admin
ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
ncs user login --username=$NCM_ADMIN_USR --password=$NCM_ADMIN_PWD

if [[ $TENANT_ENABLED == "true" ]]; then
	existTenant=$(ncs kubectl get tenant | grep $TENANT_NAME-admin )
	if [[  $existTenant == "" ]]; then
		# create tenant
		if [ ! -f "${TENANT_NAME}_tenant.json" ]; then
			jsonFile="{ \"name\": \"$TENANT_NAME\", \"requireNamespacePrefix\": false, \"harborProjectQuota\": 25000, \"resourceQuota\": {}, \"limitRange\": { \"limits\": [] } }"
			echo $jsonFile > $scriptHome/${TENANT_NAME}_tenant.json
		fi

		ncs tenant create --config $scriptHome/${TENANT_NAME}_tenant.json
		if [[ $? -ne 0 ]]; then
        		echo "Failed to execute tenant create command."
        		exit 1
    		fi


		resetCmd=$(ncm user login --username=$TENANT_NAME-admin --password='ncs@CSF_k8s' | tail -1)
		$resetCmd$TENANT_ADMIN_PWD
		if [[ $? -ne 0 ]]; then
                        echo "Failed to reset pwd for tenant $TENANT_NAME."
                        exit 1
                fi
	fi
	echo "Tenant is $TENANT_NAME for $VNFID"

else
	existNs=$(ncs kubectl get ns | grep -w ${HSS_NAMESPACE})
	if [[  $existNs == "" ]]; then
		ncs kubectl create ns $HSS_NAMESPACE
	fi
	echo "namespace is $HSS_NAMESPACE for $VNFID."
fi
