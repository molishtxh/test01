#!/bin/bash
k=1100000000
work_dir=$(cd `dirname $0`; pwd)
target_dir="/srv/sftp/bulk-sftp-DEFAULT"
mkdir -p ${work_dir}/backup_create
chown provgw:provgw ${work_dir}/backup_create
echo "==last sub.res time== "`ls -lhtr ${target_dir}/outbox/sub_*` >> ${target_dir}/log_provision
rm -rf ${target_dir}/outbox/sub_* ${work_dir}/backup_create/*
for (( i1=0; i1<${1}; i1+=50000 ))
do
start_sub=$(($k+$i1))
cat << EOF > ${work_dir}/backup_create/sub_create${1}_${start_sub}.spml
<?xml version="1.0" encoding="UTF-8"?>
<spml:batchRequest
    onError="exit_commit"
    processing="sequential"
    xmlns:spml="urn:siemens:names:prov:gw:SPML:2:0"
    xmlns:subscriber="urn:siemens:names:prov:gw:UNIFIED_SUB_3GPPHSS:1:0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<version>UNIFIED_SUB_3GPPHSS_v10</version>
EOF
for (( i2=0; i2<50000; i2++ ))
do
j=$(($k+$i1+$i2))
if [ $j -ge $(($k+${1})) ];then
break
fi
cat << EOF >> ${work_dir}/backup_create/sub_create${1}_${start_sub}.spml
<request xsi:type="spml:AddRequest" returnResultingObject="none">
<version>UNIFIED_SUB_3GPPHSS_v10</version>
<object xsi:type="subscriber:Subscriber">
    <identifier>26375${j}</identifier>
    <auc>
        <imsi>26375${j}</imsi>
        <encKey>BB11F0CE7CF44D78D140541FC028A290</encKey>
        <algoId>3</algoId>
        <kdbId>1</kdbId>
        <acsub>2</acsub>
        <amf>0000</amf>
        <sqn>0000003781AD</sqn>
    </auc>
    <hlr>
        <imsi>26375${j}</imsi>
        <umtsSubscriber>
            <accTypeGSM>true</accTypeGSM>
            <accTypeGERAN>true</accTypeGERAN>
            <accTypeUTRAN>true</accTypeUTRAN>
        </umtsSubscriber>
        <odboc>0</odboc>
        <odbic>0</odbic>
        <odbgprs>0</odbgprs>
        <sr>1</sr>
        <ts21/>
        <ts22/>
        <gprs>
            <msisdn>49111${j}</msisdn>
        </gprs>
        <pdpContext>
            <id>1</id>
            <qosProfile>EXTEND42</qosProfile>
        </pdpContext>
        <pdpContext>
            <id>26</id>
            <qosProfile>alphaqos</qosProfile>
        </pdpContext>
        <eps>
            <defaultPdnContextId>1</defaultPdnContextId>
            <maxBandwidthUp>4294967000</maxBandwidthUp>
            <maxBandwidthDown>4294967000</maxBandwidthDown>
            <sessionTransferNumber>12345</sessionTransferNumber>
            <msisdn>49111${j}</msisdn>
            <defaultNonIpPdnContextId>19</defaultNonIpPdnContextId>
            <extMaxBandwidthUp>9765620</extMaxBandwidthUp>
            <extMaxBandwidthDown>9765620</extMaxBandwidthDown>
        </eps>
        <epsPdnContext>
            <apn>fast.t-mobile.com</apn>
            <contextId>1</contextId>
            <type>both</type>
            <pdnGw>topon.s5pgwvapgw200.vapcf200.nrf.ne.node.epc.mnc75.mcc263.3gppnetwork.org</pdnGw>
            <pdnGwRealm>epc.mnc75.mcc263.3gppnetwork.org</pdnGwRealm>
            <pdnGwDynamicAllocation>true</pdnGwDynamicAllocation>
            <vplmnAddressAllowed>false</vplmnAddressAllowed>
            <maxBandwidthUp>4294967000</maxBandwidthUp>
            <maxBandwidthDown>4294967000</maxBandwidthDown>
            <qos>fast-test</qos>
            <extMaxBandwidthUp>9765620</extMaxBandwidthUp>
            <extMaxBandwidthDown>9765620</extMaxBandwidthDown>
            <eps5gInterworkIndicator>1</eps5gInterworkIndicator>
        </epsPdnContext>
        <epsPdnContext>
            <apn>ims</apn>
            <contextId>19</contextId>
            <type>both</type>
            <pdnGw>topon.s5pgw.vapcf200.nrf.ne.node.epc.mnc75.mcc263.3gppnetwork.org</pdnGw>
            <pdnGwRealm>epc.mnc75.mcc263.3gppnetwork.org</pdnGwRealm>
            <pdnGwDynamicAllocation>true</pdnGwDynamicAllocation>
            <vplmnAddressAllowed>false</vplmnAddressAllowed>
            <maxBandwidthUp>100000000</maxBandwidthUp>
            <maxBandwidthDown>100000000</maxBandwidthDown>
            <qos>fast-test</qos>
            <nonIpPdnTypeIndicator>true</nonIpPdnTypeIndicator>
            <nonIpDataDeliveryMech>SCEF-BASED-DATA-DELIVERY</nonIpDataDeliveryMech>
            <scefIdentity>GTMLink2.ipslgt321.S6t.HSS.bangm.nsn-rdnet.com</scefIdentity>
            <scefRealm>ipslgt321.S6t.HSS.bangm.nsn-rdnet.com</scefRealm>
            <eps5gInterworkIndicator>1</eps5gInterworkIndicator>
        </epsPdnContext>
    </hlr>
    <hss>
        <subscriptionId>1</subscriptionId>
        <profileType>normal</profileType>
        <privateUserId>
            <privateUserId>26375${j}@vzims.com</privateUserId>
            <provisionedImsi>
                <provisionedImsi>26375${j}</provisionedImsi>
            </provisionedImsi>
            <msisdn>49111${j}</msisdn>
            <preferredAuthenticationScheme>aka</preferredAuthenticationScheme>
        </privateUserId>
        <implicitRegisteredSet>
            <irsId>IRS9999</irsId>
        </implicitRegisteredSet>
        <publicUserId>
            <originalPublicUserId>sip:+26375${j}@vzims.com</originalPublicUserId>
            <barringIndication>false</barringIndication>
            <defaultIndication>true</defaultIndication>
            <serviceProfileName>SP0</serviceProfileName>
            <irsId>IRS9999</irsId>
            <displayNamePrivacy>false</displayNamePrivacy>
            <aliasId>1</aliasId>
        </publicUserId>
        <serviceProfile>
            <profileName>SP0</profileName>
            <mandatoryCapability>
                <mandatoryCapability>3</mandatoryCapability>
            </mandatoryCapability>
            <mandatoryCapability>
                <mandatoryCapability>4</mandatoryCapability>
            </mandatoryCapability>
            <globalFilterId>
                <globalFilterId>TTNOrigMsgRPAck4</globalFilterId>
            </globalFilterId>
            <subscribedMediaProfileID>
                <sessionReleasePolicy>deregisterForcedSessionRelease</sessionReleasePolicy>
                <forkingPolicy>noForking</forkingPolicy>
            </subscribedMediaProfileID>
            <userFilterCriteria>
                <filterName>MessageRegister</filterName>
                <asSipAddress>sip:imp.sip.t-mobile.com</asSipAddress>
                <priority>30</priority>
                <triggerPoints>
                    <![CDATA[<TriggerPoint><ConditionTypeCNF>1</ConditionTypeCNF><SPT><ConditionNegated>0</ConditionNegated><Group>0</Group><Method>REGISTER</Method><Extension><RegistrationType>0</RegistrationType></Extension></SPT><SPT><ConditionNegated>0</ConditionNegated><Group>0</Group><Method>REGISTER</Method><Extension><RegistrationType>1</RegistrationType></Extension></SPT><SPT><ConditionNegated>0</ConditionNegated><Group>0</Group><Method>REGISTER</Method><Extension><RegistrationType>2</RegistrationType></Extension></SPT><SPT><ConditionNegated>0</ConditionNegated><Group>1</Group><SIPHeader><Header>Contact</Header><Content>.*g\.3gpp\.smsip.*</Content></SIPHeader></SPT><SPT><Group>1</Group><SIPHeader><Header>Contact</Header><Content>.*expires=0.*</Content></SIPHeader></SPT></TriggerPoint>]]>
                </triggerPoints>
                <serviceInformation>MSISDN=49111${j},IMSI=26375${j}</serviceInformation>
                <handling>continue</handling>
                <profilePartIndication>registered</profilePartIndication>
            </userFilterCriteria>
        </serviceProfile>
        <aliasGroup>
            <aliasId>1</aliasId>
            <serviceProfileName>SP0</serviceProfileName>
            <irsId>IRS9999</irsId>
        </aliasGroup>
        <aliasRepositoryData>
            <serviceIndId>IMS-CAMEL-Services</serviceIndId>
            <asData>
                <![CDATA[<im-csi-information xsi:schemaLocation="http://uri.etsi.org/ngn/params/xml/simservs/xcap" xmlns="http://uri.etsi.org/ngn/params/xml/simservs/xcap" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><supported-imssf-camel-phases>phase4</supported-imssf-camel-phases><camel-subscription-info><o-IM-CSI><o-bcsm-camel-TDP-data-list><o-bcsm-camel-TDP-data><o-bcsm-trigger-detection-point>collected-info</o-bcsm-trigger-detection-point><service-key>30</service-key><gsm-SCF-address>14044551412</gsm-SCF-address><default-call-handling>continue-call</default-call-handling></o-bcsm-camel-TDP-data></o-bcsm-camel-TDP-data-list><camel-capability-handling>2</camel-capability-handling><csi-active></csi-active></o-IM-CSI><o-IM-bcsm-camel-TDP-criteria-list><o-IM-bcsm-camel-TDP-criteria><o-bcsm-trigger-detection-point>collected-info</o-bcsm-trigger-detection-point><destination-number-criteria><destination-number-list/><destination-number-length-list/></destination-number-criteria></o-IM-bcsm-camel-TDP-criteria></o-IM-bcsm-camel-TDP-criteria-list><vt-IM-CSI><t-bcsm-camel-TDP-data-list><t-bcsm-camel-TDP-data><t-bcsm-trigger-detection-point>term-attempt-authorized</t-bcsm-trigger-detection-point><service-key>34</service-key><gsm-SCF-address>14044551412</gsm-SCF-address><default-call-handling>release-call</default-call-handling></t-bcsm-camel-TDP-data></t-bcsm-camel-TDP-data-list><camel-capability-handling>2</camel-capability-handling><csi-active></csi-active></vt-IM-CSI><vt-bcsm-camel-TDP-criteria-list><vt-bcsm-camel-TDP-criteria><t-bcsm-trigger-detection-point>term-attempt-authorized</t-bcsm-trigger-detection-point></vt-bcsm-camel-TDP-criteria></vt-bcsm-camel-TDP-criteria-list></camel-subscription-info></im-csi-information>]]>
            </asData>
            <aliasId>1</aliasId>
        </aliasRepositoryData>
        <aliasRepositoryData>
            <serviceIndId>IMS-ODB-Information</serviceIndId>
            <asData>
                <![CDATA[<OdbForImsOrientedServices xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><OdbForImsMultimediaTelephonyServices/></OdbForImsOrientedServices>]]>
            </asData>
            <aliasId>1</aliasId>
        </aliasRepositoryData>
    </hss>
</object>
</request>
EOF
done
cat << EOF >> ${work_dir}/backup_create/sub_create${1}_${start_sub}.spml
</spml:batchRequest>
EOF
chown provgw:provgw ${work_dir}/backup_create/sub_create${1}_${start_sub}.spml
echo "==========sub_create${1}_${start_sub}.spml start time========== "`date "+%Y-%m-%d %H:%M"` >> ${target_dir}/log_provision
su - provgw -c "cp ${work_dir}/backup_create/sub_create${1}_${start_sub}.spml ${target_dir}/inbox/"
done