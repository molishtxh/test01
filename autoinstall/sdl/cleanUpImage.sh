#!/bin/bash

set -x
CONTROL_IP=$1
BCMT_PORTAL_PORT=$2
NCM_ADMIN_USR=$3
NCM_ADMIN_PWD=$4
SDL_IMAGE_TAG=$5
PWD_IMAGE_TAG=$6

#scriptHome=$(cd "$(dirname "$0")";pwd)
#echo $scriptHome
#source $scriptHome/${2}

cleanUpImages(){

    # change to use ncm admin user
    ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
    ncs user login --username=$NCM_ADMIN_USR --password=$NCM_ADMIN_PWD

    echo "Starting to delete SDL images..."
    sdlImageList="
	nokia/sdl/cas
	nokia/sdl/diag
	nokia/sdl/disco
	nokia/sdl/sdl-hook
	nokia/sdl/ntf
	nokia/sdl/oes
	nokia/sdl/rtdb
	nokia/sdl/rtdblookup
	nokia/sdl/sdl-sec
	nokia/sdl/sync
	nokia/sdl/tsa
	nokia/sdl/ztshook
        "
    echo "Images to be deleted:"
    echo "$sdlImageList"

    for sdlImage in $sdlImageList;
        do
        echo "Starting to delete images $sdlImage"
            #ncs tenant-app-resource image delete --tenant_name $TENANT_NAME --image_name $image --tag_name $IMAGE_TAG
            ncs app-resource image delete --images $sdlImage:$SDL_IMAGE_TAG
            echo " Successfully delete image $sdlImage"
        done

    echo "Successfully delete images from repo."

    echo "Starting to delete SDL images..."
    pgwImageList="
	nokia/pgw/pgwbulk
	nokia/pgw/pgwcas
	nokia/pgw/pgwcore
	nokia/pgw/pgwli
	nokia/pgw/pgwoes
	nokia/pgw/sdl-sec
	nokia/pgw/tsa
        "
    echo "Images to be deleted:"
    echo "$pgwImageList"

    for pgwImage in $pgwImageList;
        do
        echo "Starting to delete images $pgwImage"
            ncs app-resource image delete --images $pgwImage:$PGW_IMAGE_TAG
            echo " Successfully delete image $pgwImage"
        done
}

cleanUpHelmCharts(){

    # change to use hss admin user
    ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
    ncs user login --username=$TENANT_ADMIN_USR --password=$TENANT_ADMIN_PWD

    chartList=$(ncs tenant-app-resource chart list --tenant_name $TENANT_NAME | grep name | awk -F ":" '{print $2}'| sed 's/\"//g' | sed 's/\,//g')
echo "$chartList"

    echo "Starting to delete charts for tenant $TENANT_NAME:"
    for chart in $chartList; do
        ncs tenant-app-resource chart delete --tenant_name $TENANT_NAME --chart_name $chart --chart_version $CHART_VERSION
    if [[ $? -eq 0 ]]; then
           echo "Successfully execute delete ${chart}, please wait..."
           sleep 5
    else
       echo "Failed to execute chart delete command."
    fi
    done

    echo "Successfully delete charts from harbor."

}

main(){
    cleanUpImages
}

main



