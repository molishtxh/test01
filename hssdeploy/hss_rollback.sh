#!/bin/bash

NAME_SPACE="ptreg"
VNFID="qdlab1"
Reversion=${1:-1}
hook_tag=""

set -x

date;helm3  rollback ${VNFID}-cluster $Reversion -n ${NAME_SPACE} $hook_tag;date
date;helm3  rollback ${VNFID}-cluster-security $Reversion -n ${NAME_SPACE} $hook_tag;date
date;helm3  rollback ${VNFID}-network $Reversion -n ${NAME_SPACE} $hook_tag;date
date;helm3  rollback ${VNFID}-dco 1 -n ${NAME_SPACE} $hook_tag;date
date;helm3  rollback ${VNFID}-etcd $Reversion -n ${NAME_SPACE} $hook_tag;date
date;helm3  rollback ${VNFID}-xds $Reversion -n ${NAME_SPACE} $hook_tag;date
date;helm3  rollback ${VNFID}-db $Reversion -n ${NAME_SPACE} $hook_tag;date
date;helm3  rollback ${VNFID}-cnsba $Reversion -n ${NAME_SPACE} $hook_tag;date
date;helm3  rollback ${VNFID} 1 -n ${NAME_SPACE} --no-hooks --timeout 15m;date
#date;helm3  rollback ${VNFID}-debugassist $Reversion -n ${NAME_SPACE} $hook_tag;date

