#!/bin/bash
netConfXML=$1

startLine=`grep -rsn "<ARPF:ARPF>" ${netConfXML} | awk '{print $1}'|awk -F":" '{print $1}'`
sed -i "${startLine}r ./softauc.xml" ${netConfXML}

S="TRIGGER:connectionSecurityMode"
bS="<"$S">"
eS="<\/"$S">"
fS="${bS}.*${eS}"

U="TRIGGER:useWhitelist"
bU="<"$U">"
eU="<\/"$U">"
fU="${bU}.*${eU}"

triggerRRS=`grep -in "<TRIGGER:serviceName>TRIGGERSERVICE<\/TRIGGER:serviceName>" $netConfXML`
let triggerRRS=`echo ${triggerRRS} |awk -F: '{print $1}'`
triggerRRE=`expr $triggerRRS + 20`
sed -i "${triggerRRS},${triggerRRE} s;${fS};${bS}0${eS};g" $netConfXML
if [[ $? -eq 0 ]]; then
   echo "## TRIGGERSERVICE connectionSecurityMode are changed successfully in the generic file  ##"
else
   echo "## TRIGGERSERVICE connectionSecurityMode are changed failure in the generic file  ##"
   exit 1
fi
sed -i "${triggerRRS},${triggerRRE} s;${fU};${bU}false${eU};g" $netConfXML
if [[ $? -eq 0 ]]; then
   echo "## TRIGGERSERVICE useWhitelist are changed successfully in the generic file ##"
else
   echo "## TRIGGERSERVICE useWhitelist are changed failure in the generic file ##"
   exit 1
fi

triggerBCS=`grep -in "<Trigger:serviceName>TRIGGERSERVICEBC<\/Trigger:serviceName>" $netConfXML`
let triggerBCS=`echo $triggerBCS |awk -F: '{print $1}'`
triggerBCE=`expr $triggerBCS + 20`
sed -i "${triggerBCS},${triggerBCE} s;${fS};${bS}0${eS};g" $netConfXML
if [[ $? -eq 0 ]]; then
   echo "## TRIGGERSERVICEBC connectionSecurityMode are changed successfully in the generic file  ##"
else
   echo "## TRIGGERSERVICEBC connectionSecurityMode are changed failure in the generic file  ##"
   exit 1
fi
sed -i "${triggerBCS},${triggerBCE} s;${fU};${bU}false${eU};g" $netConfXML
if [[ $? -eq 0 ]]; then
   echo "## TRIGGERSERVICEBC useWhitelist are changed successfully in the generic file ##"
else
   echo "## TRIGGERSERVICEBC useWhitelist are changed failure in the generic file ##"
   exit 1
fi

triggerBCHS=`grep -in "<Trigger:serviceName>TRIGGERSERVICEBCH<\/Trigger:serviceName>" $netConfXML`
let triggerBCHS=`echo $triggerBCHS |awk -F: '{print $1}'`
triggerBCHE=`expr $triggerBCHS + 20`
sed -i "${triggerBCHS},${triggerBCHE} s;${fS};${bS}0${eS};g" $netConfXML
if [[ $? -eq 0 ]]; then
   echo "## TRIGGERSERVICEBCH connectionSecurityMode are changed successfully in the generic file  ##"
else
   echo "## TRIGGERSERVICEBCH connectionSecurityMode are changed failure in the generic file  ##"
   exit 1
fi
sed -i "${triggerBCHS},${triggerBCHE} s;${fU};${bU}false${eU};g" $netConfXML
if [[ $? -eq 0 ]]; then
   echo "## TRIGGERSERVICEBCH useWhitelist are changed successfully in the generic file ##"
else
   echo "## TRIGGERSERVICEBCH useWhitelist are changed failure in the generic file ##"
   exit 1
fi

triggerRRHS=`grep -in "<TRIGGER:serviceName>TRIGGERSERVICEH<\/TRIGGER:serviceName>" $netConfXML`
let triggerRRHS=`echo ${triggerRRHS} |awk -F: '{print $1}'`
triggerRRHE=`expr $triggerRRHS + 20`
sed -i "${triggerRRHS},${triggerRRHE} s;${fS};${bS}0${eS};g" $netConfXML
if [[ $? -eq 0 ]]; then
   echo "## TRIGGERSERVICEH connectionSecurityMode are changed successfully in the generic file  ##"
else
   echo "## TRIGGERSERVICEH connectionSecurityMode are changed failure in the generic file  ##"
   exit 1
fi
sed -i "${triggerRRHS},${triggerRRHE} s;${fU};${bU}false${eU};g" $netConfXML
if [[ $? -eq 0 ]]; then
   echo "## TRIGGERSERVICEH useWhitelist are changed successfully in the generic file ##"
else
   echo "## TRIGGERSERVICEH useWhitelist are changed failure in the generic file ##"
   exit 1
fi

