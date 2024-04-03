# -*- coding: utf-8 -*-
"""
Created on Fri May  6 13:27:33 2022

@author: kumarz
"""
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

from nltk.tokenize import word_tokenize
import nltk
#nltk.download('punkt')

import requests
from requests.auth import HTTPBasicAuth
import json

import os
import logging

from config import JIRA_ACCOUNT,JIRA_PWD,JIRA_URL,JQL,MIN_ALPHA,EPOCHS_LIST,SIZE_LIST,ALPHA_LIST,DM_LIST
from config import set_logger

logger = logging.getLogger(__name__)

auth = HTTPBasicAuth(JIRA_ACCOUNT,JIRA_PWD)
headers = {"Accept": "application/json"}
   
def getAllJIRA():    
    url = JIRA_URL + 'search'
    query = {
        'jql': JQL,
        'startAt': 0,
        'maxResults': 100,
    }
    # Create a request object with above parameters.
    response = requests.request("GET", url, headers=headers,auth=auth,params=query)
    projectIssues = json.dumps(json.loads(response.text),sort_keys=True,indent=4,separators=(",", ": "))
    dictProjectIssues = json.loads(projectIssues)
    jiraList = filter_crawler(dictProjectIssues)
    totalNo = dictProjectIssues["total"]
    logger.warning(f" total jira number is:{dictProjectIssues['total']}")
    for i in range(int(int(totalNo)/100)):
        query = {
            'jql': JQL,
            'startAt': i*100 +100,
            'maxResults': 100,
        }
        response = requests.request("GET", url, headers=headers,auth=auth,params=query)
        singleRoundIssues = json.dumps(json.loads(response.text),sort_keys=True,indent=4,separators=(",", ": "))
        singleDicIssues = json.loads(singleRoundIssues)
        logger.warning(f"round {i}: jiralist length is {len(jiraList)}")
        for key, value in singleDicIssues.items():
            if(key == "issues"):
                totalIssues = len(value)
                for eachIssue in range(totalIssues):
                    jiraList.append(iterateDictIssues(value[eachIssue]))
    logger.warning(f" dumped JIRA number in dictProjectIssues is:{len(jiraList)}")
    return jiraList

def iterateDictIssues(issue):
#    logger.warning(f"issue key is: {issue['key']}")
#    logger.warning(f"issue summary is: {issue['fields']['summary']}")
    if "description" in issue["fields"]:
#        logger.warning(f"issue description is: {issue['fields']['description']}")
        summary_content = issue["fields"]["description"]
        default_content = "Please enter the fault support description here      Please provide any details you find relevant about the customer environment here E.g.       Product cluster and configuration    Hosting Labs    Its composition    Hardware virtualized environment details    OS    Networking    Hotfixes workaround applied    TSN applied    Etc..."
        if default_content in preHandle(summary_content):
            summary_content = ""
        if "customfield_37638" in issue["fields"] and issue["fields"]["customfield_37638"] is not None:
            summary_content = " " + issue["fields"]["customfield_37638"]
    else:
        summary_content = ""
    ticket_dict = {'jiraid': issue["key"], 'title': preHandle(issue["fields"]["summary"]), 'summary': preHandle(summary_content)}
    return ticket_dict

def filter_crawler(dictProjectIssues):
    tickets_corpus = []
    for key, value in dictProjectIssues.items():
        # Issues fetched, are present as list elements,
        # against the key "issues".
        # data looks like {"expand":"schema,names","startAt":0,"maxResults":50,"total":963,"issues":[{},{}]}
        if(key == "issues"):
            totalIssues = len(value)
            for eachIssue in range(totalIssues):
#                logger.warning(f"issue number is: {eachIssue}")
                tickets_corpus.append(iterateDictIssues(value[eachIssue]))
    return tickets_corpus

def preHandle(txt):
    if txt is None:
        txt = ""
        return txt
    txt=txt.replace("\n", " ")
    txt=txt.replace("--", " ")
    txt=txt.replace("===", " ")
    txt=txt.replace(". ", " ")
    txt=txt.replace('\t',' ').replace('\r\n',' ').replace('\r',' ')
    for ch in '~!@#$%^&*()+"{}[]|?<>\'/:;_':
        txt=txt.replace(ch," ")
    return txt

def train_doc2vec_model(model_name_prefix,tagged_data, vec_size, alpha, min_word_count_per_doc, dm, no_of_epochs):
    model = Doc2Vec(vector_size=vec_size,
                alpha=alpha, 
                min_alpha=MIN_ALPHA,
                min_count=min_word_count_per_doc,
                dm =dm,
                workers = 4)
    model.build_vocab(tagged_data)
    model.train(tagged_data, total_examples=model.corpus_count, epochs=no_of_epochs)
    modelname = model_name_prefix+"_d2v_"+str(dm)+"dm_"+str(no_of_epochs)+"epoch_"+str(vec_size)+"vecsize_"+str(alpha)+"alpha.model"
    model.save("./models/{}".format(modelname))
    logger.warning(f" Model trained: {modelname}")
    
if __name__ == '__main__':
    set_logger("model_Train")
    fnb_tickets_corpus = getAllJIRA()
    tagged_data_only_summary = [TaggedDocument(words=word_tokenize((str(ticket_dict['title'])+" "+str(ticket_dict['summary'])).lower()), tags=[str(ticket_dict['jiraid'])]) for ticket_dict in fnb_tickets_corpus]

    isExists=os.path.exists("models")
    if not isExists:
        os.makedirs("models")

    for vec_size in SIZE_LIST:
        for alpha in ALPHA_LIST:
            for epoch in EPOCHS_LIST:
                for dm in DM_LIST:
                    train_doc2vec_model(str(1)+"_summary",tagged_data_only_summary, vec_size, alpha, 1, dm, epoch)
