#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import logging

JIRA_ACCOUNT = "retong"
JIRA_PWD = "Txh987987"

JIRA_URL = "https://jiradc2.ext.net.nokia.com/rest/api/2/"
JQL = 'project IN (HSSFM, UDMFM, HLRFM)'#add your project into () and seperate it with ','

SIMILARITY_THRESHOLDS = 0.7
MAX_RECOMMENDING_JIRA_NUM = 3
RECOMMEND_THRESHOLDS = 2

MIN_ALPHA = 0.0001
EPOCHS_LIST = [100,500]#[100,500,1000]
SIZE_LIST = [50,100,200]#[10,50,100,200]
ALPHA_LIST = [0.025]#[0.05, 0.01, 0.025]
DM_LIST = [0,1]

logger = logging.getLogger(__name__)

def set_logger(log_File_name):
    """ Set logger """
    logger.setLevel(logging.WARNING)

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.WARNING,
        handlers=[
            logging.FileHandler(
                filename=f"{log_File_name}.log",
                mode="w",
                encoding="utf-8", )
        ], )
    # create console handler and set level to debug
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level=logging.WARNING)
    # add formatter to console_handler
    console_handler.setFormatter(fmt=logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    # add console_handler to logger
    logger.addHandler(console_handler)
