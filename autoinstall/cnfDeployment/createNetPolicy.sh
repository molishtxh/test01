#!/bin/sh
scriptHome=$(cd "$(dirname "$0")";pwd)
source $scriptHome/${1}

if [ $TENANT_ENABLED == "false" ]; then
    echo "Not need to create Network Policy."
    exit 0
fi

#login with ncm-admin
ncs config set --endpoint=https://$CONTROL_IP:$BCMT_PORTAL_PORT/ncm/api/v1
ncs user login --username=$NCM_ADMIN_USR --password=$NCM_ADMIN_PWD

cat << EOF > /tmp/networkpolicy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ${ZTS_NAMESPACE}-${TENANT_NAME}
  namespace: ${ZTS_NAMESPACE}
spec:
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          mt.ncm.nokia.com/tenant: ${TENANT_NAME}
      podSelector: {}
  podSelector: {}
  policyTypes:
  - Ingress

EOF

ncs kubectl get namespace ${ZTS_NAMESPACE} -o yaml|grep -i tenant
if [ $? != 0 ]; then
    echo "Not need to create Network Policy as ZTS namespace is not TENANT enabled."
    exit 0
fi

ncs kubectl get networkpolicy -n ${ZTS_NAMESPACE} -o yaml|grep -i "mt.ncm.nokia.com/tenant: ${TENANT_NAME}$"
if [ $? != 0 ]; then
    ncs kubectl apply -f /tmp/networkpolicy.yaml
    if [ $? != 0 ]; then
        echo "Create network policy failed, please check"
        exit 1
    fi
    echo "Create network policy successed"
fi
exit 0
    
