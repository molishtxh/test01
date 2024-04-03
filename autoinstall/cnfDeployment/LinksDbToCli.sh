#!/bin/bash
#####=================================================
##### DbToCli.sh
#####=================================================
#####=================================================

EXIT_ON_ERR=1
WAIT_FOR_EACH_CMD=0
Count_Total=0
Count_Success=0

exec_cli()
{
   ((Count_Total++))
    echo "Executing CLI : $*"
   $*
   if [ $? -eq 0 ]
   then
   ((Count_Success++))
      sleep $WAIT_FOR_EACH_CMD
   elif [ $EXIT_ON_ERR -ne 0 ]
   then
       echo  "Cli Executed : $Count_Total"
       echo  "Successful : $Count_Success"
       echo  "Fail : `expr $Count_Total - $Count_Success` "
      exit $EXIT_ON_ERR
   fi
}
Usage()
{
   name=`basename $0`
   if [ $PAM_ENABLE -eq 1 ]
   then
      echo "Usage : $name [-n userName] [-w password ]"
   else
      echo "Usage : $name -n <userName> [-w password ]"
   fi
      echo "-n, --userName     User Name"
      echo "-w, --password     User's password"
      echo "                   Do not use this option(-w) if no password is set"
      exit 2 ;
}




if [ $# -eq 0 -a $PAM_ENABLE -eq 0 ]
 then
       Usage
fi

           n_flag=0
           w_flag=0
while getopts n:w:h OPTION
   do
      case ${OPTION} in
         n) n_flag=1
         ;;
   w) w_flag=1
      ;;
   h) Usage
      ;;
   \?) echo "ERROR: Invalid data entered"
      exit 2
      ;;
   esac
      done
if [ $PAM_ENABLE -eq 0 -a $n_flag -eq 0 ]
   then
      echo "ERROR : Username must be provided"
      Usage
fi



###### ADMIN LOGIN COMMAND ######

exec_cli Login $*

###### ROUTESET DETAILS ######

exec_cli AddRouteset -N N1_PC1001_RS_SPOPC -v ITU -o 1001 -d 1001 -f 0 -t SPOPC -a 0 --rq NO --ssf NATIONAL --tb YES --ps NO --us YES --ma YES
exec_cli AddRouteset -N N1_PC1001_WEISZ_rs -v ITU -o 1001 -d 9997 -f 1 -t SP -a 0 --rq NO --tb YES --ps NO --us YES --ma YES

###### LINKSET DETAILS ######

exec_cli AddLinkset -M N1_PC1001_WEISZ_ls -v ITU -o 1001 -d 9997 -a 0

###### ROUTE DETAILS ######


exec_cli AddRoute -N N1_PC1001_WEISZ_rs -M N1_PC1001_WEISZ_ls -p 0

###### TRUNK DETAILS ######


###### LINK DETAILS ######

exec_cli AddLink -m N1_PC1001_WEISZ_link -M N1_PC1001_WEISZ_ls -t 2 -C MTP2 -T 1 -p 0 -S ACTIVATED

###### SCCP NODE ######

exec_cli AddSccpNode -n N1_PC1001_HLR -v ITU -o 1001 -d 1001 -F FALSE -a 0 -Y FALSE -y FALSE
exec_cli AddSccpNode -n N1_PC1001_WEISZ_node -v ITU -o 1001 -d 9997 -F FALSE -a 0 -Y FALSE -y FALSE

###### SCCP NODE SSN ######

exec_cli AddSccpNodeSsn -n N1_PC1001_WEISZ_node -s 7
exec_cli AddSccpNodeSsn -n N1_PC1001_WEISZ_node -s 8
exec_cli AddSccpNodeSsn -n N1_PC1001_WEISZ_node -s 145
exec_cli AddSccpNodeSsn -n N1_PC1001_WEISZ_node -s 147
exec_cli AddSccpNodeSsn -n N1_PC1001_WEISZ_node -s 149

###### SCCP APPLICATION GROUP ######

exec_cli AddSccpAppGroup -n HLR -v ITU -D LOADSHARE -a 0

###### SCCP NODE GROUP MEMBER ######

exec_cli AddSccpAppGroupMember -n HLR -v ITU -m N1_PC1001_HLR -s 6 -c 0 -C FALSE

###### SCCP CONVERSION MAP ######


###### CONVERSION PROCEDURE ######

exec_cli AddGtConversionProcedure -n N1_PC1001_GTPROC -v ITU -a 0 -r 1 -u UNKNOWN -t 0 -f NATIONAL -O COPY_DIGITS -R FALSE -T TRUE -F TRUE -U TRUE
exec_cli AddGtConversionProcedure -n N1_PC1001_GTPROC_TMP -v ITU -a 0 -r 1 -u UNKNOWN -t 10 -f NATIONAL -O COPY_DIGITS -R FALSE -T TRUE -F TRUE -U TRUE

###### GT SELECTOR ######

exec_cli AddGtSelector -n N1_PC1001_GTSEL -v ITU -a 0

###### GTA MAP ######

exec_cli AddGta -g 49194982 -o ALL -v ITU -a 0 -n N1_PC1001_GTSEL -y TRUE -F FALSE -t DPC -m N1_PC1001_HLR -s 6 -T DPC_SSN -M N1_PC1001_GTPROC_TMP -e NATIONAL
exec_cli AddGta -g 49170440 -o ALL -v ITU -a 0 -n N1_PC1001_GTSEL -y TRUE -F FALSE -t DPC -m N1_PC1001_HLR -s 6 -T DPC_SSN -M N1_PC1001_GTPROC_TMP -e NATIONAL
exec_cli AddGta -g 49194 -o 1001 -v ITU -a 0 -n N1_PC1001_GTSEL -y FALSE -F FALSE -t DPC -m N1_PC1001_WEISZ_node -C TRUE -T GT -M N1_PC1001_GTPROC -e INTERNATIONAL
exec_cli AddGta -g 49171 -o 1001 -v ITU -a 0 -n N1_PC1001_GTSEL -y FALSE -F FALSE -t DPC -m N1_PC1001_WEISZ_node -C TRUE -T GT -M N1_PC1001_GTPROC -e INTERNATIONAL

###### SCCP APP INST MON DATA ######


###### ISUP CIC MAP ######


###### ISUP NODE ######


###### ISUP OPC-DPC CIC MAP ######


###### M2PA LSP ######


###### M2PA PSP ######


###### M2PA LINK ######


###### UA SG MODE (CLI for local SG stack) ######


###### UA SG ######


###### UA SGP ######


###### UA AS ######


###### UA ASP ######


###### UA AS MODE (CLI for local AS stack) ######


###### UA ASP ######

exec_cli AddAsp -z M3UA -n N1_PC1001_FE82ASP -j 2 -i SIGPIP -c 17 -C 17 -P 2907 -f 0 -t local --dscp BE

###### UA AS ######

exec_cli AddAs -N N1_PC1001_FE82AS -z M3UA -j ITU_NW -D OVERRIDE -d 1001 -f FALSE -t LOCAL

###### UA SG ######

exec_cli AddSg -M N1_PC1001_WEISZ_sg -z M3UA -t REMOTE

###### UA SGP ######

exec_cli AddSgp -z M3UA -m N1_PC1001_WEISZ_sgp -M N1_PC1001_WEISZ_sg -i LPCIP -P 50348 -t REMOTE

###### UA IPSP MODE (CLI for IPSP stack) ######


###### UA LOCAL IPSP ######


###### UA Peer IPSP ######


###### UA AS ######


###### UA LocalIPSP-PeerIPSP ######


###### UA REM IPSP AS ######


###### UA AS-SG ######

exec_cli AssociateAsToSg -N N1_PC1001_FE82AS -M N1_PC1001_WEISZ_sg -r 2 -c 1 -t SLS

###### UA ASP AS ######


###### ASM ROUTE ######

exec_cli AddASMRoute -M N1_PC1001_WEISZ_sg -z M3UA -N N1_PC1001_WEISZ_rs -p 0

###### SCTP PARAMETERS DETAILS ######

##+-----------+--------+------+-------+
##|Parameter  | Low    | High |Current|
##+-----------+--------+------+-------+
## RtoMin    1       60000    500
## RtoMax    1       60000000    1000
## HbInterval    0       86400000    1000
## PathMaxRxt    1       10    3
## InitAttempts    1       10    5

###### UA ASP-SGP ######

exec_cli AssociateAspToSgp -n N1_PC1001_FE82ASP -m N1_PC1001_WEISZ_sgp -S UA_ENABLED -i LPCIP --rtoMin 500 --rtoMax 1000 --hbInterval 1000 --pathMaxRtx 3 --initAttempts 5 --congQueueThresholdLen 100 --congQueueMaxLen 1000 --congLvl1Onset 30 --congLvl2Onset 50 --congLvl3Onset 70 --congLvl1Abate 20 --congLvl2Abate 40 --congLvl3Abate 60

###### UA PXY RTNG INTF ######


###### CONVERSION RULE ######


###### G S ######


###### LINKSET GS ######


###### GS METER ######


###### OVLC TRIGGER ######

exec_cli ModifyOvlcTrigger -j USED_BUF -S ENABLE -e 30 -l 5 -b 40

###### ADMIN LOGOUT COMMAND ######

exec_cli Logout

