#!/bin/bash

set -x

EXPS_TO_BE_INSTALLED_PATH="${1}"
EXPS_SEQUENCE="${2}"
pgwops_user="${3}"
pgwops_pwd="${4}"
pgwops="${5}"
pgw_pwd="${6}"
pgw="${7}"

#echo $EXPS_TO_BE_INSTALLED_PATH

##step1: untar##
cd $EXPS_TO_BE_INSTALLED_PATH

#for file in `ls $EXPS_TO_BE_INSTALLED_PATH`  
#do
#if [ -d $EXPS_TO_BE_INSTALLED_PATH"/"$file ] 
#then
#   echo $EXPS_TO_BE_INSTALLED_PATH"/"$file "is a directory"
#else
#   echo $EXPS_TO_BE_INSTALLED_PATH"/"$file
#   tar -xvf $EXPS_TO_BE_INSTALLED_PATH"/"$file
#fi
#done

for file in `ls $EXPS_TO_BE_INSTALLED_PATH`
do
   restut=$(echo $file | grep ".tar")
   if [[ "$restut" != "" ]];then
     tar -xvf $EXPS_TO_BE_INSTALLED_PATH"/"$file
   fi
done


#step2: get releate xml, and netconf this file#
filePath=$EXPS_TO_BE_INSTALLED_PATH"/AdditionalData/"
cp netconf-console $filePath
cd $filePath

for file in `ls $filePath`
do
   restut=$(echo $file | grep ".xml")
   if [[ "$restut" != "" ]];then
        echo "get xml file：$file"
#        for exp in ${EXPS_SEQUENCE}; do
#            checkres=$(echo $file | grep -i ${exp})
#            if [[ "$checkres" != "" ]]
#            then
#                echo "get needed xml file：$file"
                sed -i 's/\<ldap-password\>.*.<\/ldap-password\>/\<ldap-password\>quP9lX09lBcejfqHTE5mGQ==\<\/ldap-password\>/g' $file
                #./netconf-console -u $pgwops_user -p $pgwops_pwd --host=$pgwops --rpc=$file
#            fi
#        done
   fi
done

#step3: for bulk.xml#
( cat <<eof
<edit-config>
    <target>
        <running/>
    </target>
    <config>
        <pgw
            xmlns=http://nokia.com/pgw>
            <config>
                <service-config>
                    <feature-control>
                        <pgw-bulk-query-notifications-mtls>TLSSELFSIGNED</pgw-bulk-query-notifications-mtls>
                    </feature-control>
                </service-config>
            </config>
        </pgw>
    </config>
</edit-config>
eof
#) >bulk.xml
) > bulk.xml 
#./netconf-console -u $pgwops_user -p $pgwops_pwd --host=$host --rpc=bulk.xml


#for lidf#
for file in `ls $filePath`
do
   restut=$(echo $file | grep ".ldif")
   if [[ "$restut" != "" ]];then
        echo "get ldif file：$file"
        sed -i 's/o=<TENANT>/o=DEFAULT/g' $file
        #ldapadd -x -c -h $pgw -p 16611 -D "cn=pgwAdminUser" -w $pgw_pwd -f $file
   fi
done

