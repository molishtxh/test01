#!/bin/bash

NAME_SPACE="hssfire"
VNFID="qdlab1"
zts_ns="zts"


set -x
helm3 uninstall ${VNFID} -n ${NAME_SPACE}
helm3 uninstall debugassist -n ${NAME_SPACE}
helm3 uninstall ${VNFID}-cnsba -n ${NAME_SPACE}
helm3 uninstall ${VNFID}-db -n ${NAME_SPACE}
helm3 uninstall nreg-hss-hlr-xds -n ${NAME_SPACE}
helm3 uninstall nreg-hss-hlr-etcd -n ${NAME_SPACE}
helm3 uninstall nreg-hss-hlr-dco -n ${NAME_SPACE}
helm3 uninstall nreg-hss-hlr-network -n ${NAME_SPACE}
helm3 uninstall nreg-hss-hlr-cluster -n ${NAME_SPACE}
helm3 uninstall nreg-hss-hlr-cluster-security -n ${NAME_SPACE}

kubectl exec -it caserver-0 -n ${zts_ns} -- sh /home/causer/del_user.sh ${VNFID}
kubectl delete job -n ${NAME_SPACE} --all
kubectl delete secrets  -n ${NAME_SPACE} --all
kubectl delete serviceaccounts -n ${NAME_SPACE} --all
#kubectl delete roles -n ${NAME_SPACE} --all
#kubectl delete rolebinding -n ${NAME_SPACE} --all

echo "=== show the current status after uninstalling ==="
kubectl get pod -n ${NAME_SPACE}
helm3 list -n ${NAME_SPACE} --all
kubectl get pvc -n ${NAME_SPACE}
kubectl get jobs -n ${NAME_SPACE}
kubectl get serviceaccounts -n ${NAME_SPACE}
kubectl get configmaps -n ${NAME_SPACE}
kubectl get secrets -n ${NAME_SPACE}
kubectl get roles -n ${NAME_SPACE}
kubectl get rolebinding -n ${NAME_SPACE}
