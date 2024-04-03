#!/usr/bin/python3

import sys
from optparse import OptionGroup, OptionParser

#specfic product
import lcmCommon
import lcmHssInstall
import lcmSdlInstall
import lcmPgwInstall

def usageMsg():
    msg = "Usage: /usr/bin/python3 lcm.py -p [Product] -m [LCMMODE]\n\n"\
          "Supported products:\n"
    for value in lcmCommon.lcmProducts:
        msg += value + "\n"
    msg += "\nSupported lcm options:\n"
    for key, value in lcmCommon.lcmOptions.items():
        msg += "  " + key + value + "\n"
    msg += "\nFor example:\n"\
           "    /usr/bin/python3 lcm.py -p HSS -m deploy\n"\
           "    /usr/bin/python3 lcm.py -P SDL -m pre_healthcheck\n"\
           "    /usr/bin/python3 lcm.py -P PGW -m deploy_only\n"
    msg += "\nPlease choose one product to see more usage message\n"
    return msg

def checkInput(parser, options):
    if not options.product or not options.lcmMode:
        parser.error("incorrect number of arguments")
        sys.exit(2)
    if options.product not in lcmCommon.lcmProducts:
        parser.error("option product is invalid")
        sys.exit(2)
    if options.lcmMode not in lcmCommon.lcmOptions.keys():
        parser.error("option lcmMode is invalid")
        sys.exit(2)

if "__main__" == __name__:
    parser = OptionParser(usageMsg())
    parser.add_option("-p", "--product", dest="product", help="Which product needs to be installed.")
    parser.add_option("-m", "--mode", dest="lcmMode", help="CNF deployment options.")
    #parser.add_option("-i", "--file", dest="fileName", help="read data from FILENAME For HSS installation")
    #parser.add_option("-y", "--file1", dest="NfileName", help="read network data from FILENAME")
    (options, args) = parser.parse_args()
    checkInput(parser, options)
    print(str(options.product) + " will be installed as " + options.lcmMode +" mode.")
    product = options.product
    lcmMode = options.lcmMode

    lcmCommon.logFile()

    if product == 'HSS':
        deployInstance = lcmHssInstall.hssInstall()
    elif product == 'SDL':
        deployInstance = lcmSdlInstall.sdlInstall()
    elif product == 'PGW':
        deployInstance = lcmPgwInstall.pgwInstall()
    
    if lcmMode == 'deploy':
        deployInstance.deployEntry()
    elif lcmMode == 'pre_healthcheck':
        deployInstance.preHealthcheckEntry()
    elif lcmMode == "prepare":
        deployInstance.prepareEntry()
    elif lcmMode == "deploy_only":
        deployInstance.deployOnlyEntry()
    elif lcmMode == "post_healthcheck":
        deployInstance.postHealthcheckEntry()
    elif lcmMode == "terminate":
        deployInstance.terminateEntry()



