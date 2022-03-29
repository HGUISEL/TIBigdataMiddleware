from datetime import datetime
import time
import json
import sys
import traceback
import os
from elasticsearch import Elasticsearch
from common import cmm
#import topic_analysis.esAccount as esAcc

sys.path.append(os.path.abspath('/home/middleware/TIBigdataMiddleware/topic_analysis'))
import esAccount as esAcc

import warnings
warnings.filterwarnings("ignore")

es = Elasticsearch(
    [esAcc.host],
    http_auth=(esAcc.id, esAcc.password),
    scheme="https",
    port= esAcc.port,
    verify_certs=False
)
index = esAcc.index

TFIDF_DIR = "./rcmdHelper/tfidfValues/"
DATA_DIR = "./rcmdHelper/data/"
RESULT_DIR = "./rcmdHelper/outputs/"
TABLE_DIR = "./rcmdHelper/tables/"

def create_similiarity(data = None):
    cosine_sim = create_similiarity_matrix(data)
    sort_similiarity_table(cosine_sim)

def makeCorpus (resp):
    corpus = []
    for oneDoc in resp['hits']['hits']:
            try: 
                if "file_extracted_content" in oneDoc["_source"].keys():
                    corpus.append(
                        {
                            "hashkey" : oneDoc["_source"]["hash_key"],
                            "post_title" : oneDoc["_source"]["post_title"],
                            "content" : oneDoc["_source"]["file_extracted_content"]
                        }
                    )
                else:
                    corpus.append(
                        {
                            "hashkey" : oneDoc["_source"]["hash_key"],
                            "post_title" : oneDoc["_source"]["post_title"],
                            "content" : oneDoc["_source"]["post_body"]
                        }
                    )
            except KeyError as e:
                continue
    return corpus

def filterEmptyDoc (corpus):
    ids = []
    titles = []
    contents = []

    for idx, doc in enumerate(corpus):
        if doc["content"] != "":
            ids.append(doc["hashkey"])
            titles.append(doc["post_title"])
            contents.append(doc["content"])
    
    return {"id" : ids, "titles" : titles, "contents" : contents}


def processData(resp):
    # Create corpus object
    corpus = makeCorpus(resp)

    return corpus

def createJson(dir, result, count):
    # Save into Json format
    with open("{dir}{num}.json".format(dir=dir, num=count), 'w', -1, "utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

analysisResult = []
count = 0
# Get first 100 data
resp = es.search( 
    
    index = index, 
    body = { "size":100, "query": { "match_all" : {} } },    
    scroll='10m'
)
#print("get first 100 data")
c = processData(resp)
createJson(DATA_DIR, filterEmptyDoc(c), count)
###original data
#analysisResult = analysisResult + c

###twice data
analysisResult = analysisResult + c + c

scrollId = resp["_scroll_id"]
while len(resp['hits']['hits']):
    count = count + 1
    #print("start set #{}".format(count))
    resp = es.scroll( 
        scroll_id = scrollId, 
        scroll='10m'
        )        

    c = processData(resp)
    createJson(DATA_DIR, filterEmptyDoc(c), count)
    ###original data
    #analysisResult = analysisResult + c
    ###twice data
    analysisResult = analysisResult + c + c

analysisResult = filterEmptyDoc(analysisResult)

# global cosine_sim
global cosine_sim

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

tfidf = TfidfVectorizer()
for i, d in reversed(list(enumerate(analysisResult['contents']))):
    if d == None:
        analysisResult['contents'].pop(i)
        analysisResult['id'].pop(i)
        analysisResult['titles'].pop(i)

print("number of documents: ", len(analysisResult['contents']))
print("Computing TF-IDF Values...")
tfidf_mtx = tfidf.fit_transform(analysisResult['contents'])
print("Computing cosine similarity...")
s_time = time.time()
cosine_sim = linear_kernel(tfidf_mtx, tfidf_mtx)
print("It took ",time.time()-s_time," seconds")
# createJson(TFIDF_DIR, cosine_sim.tolist(), count)

import operator
    
sort_cos_sim = []
#print("create table")
for i,oneDocRec in enumerate(cosine_sim):
    oneDocRec = list(enumerate(oneDocRec))
    sort_cos_sim.append(sorted(oneDocRec, key=lambda x: x[1], reverse=True)[:20])
    createJson(TABLE_DIR, sorted(oneDocRec, key=lambda x: x[1], reverse=True)[:20], i)

#print("get result and create json")
#print(len(sort_cos_sim))
#print(len(analysisResult['id']))

for index, id in enumerate(analysisResult['id']):
    rcmdTbl = sort_cos_sim[index]
    rcmdList = []
    for i, oneRcmd in enumerate(rcmdTbl):
        if i == 0 :
            continue
        docIdx = oneRcmd[0]
        rcmdList.append([analysisResult["id"][docIdx], oneRcmd[1]])
        oneDocRcmd = {"hashkey" : id, "rcmd" : rcmdList}
    createJson(RESULT_DIR, [oneDocRcmd], index)

#print("Done")
cmm.showTime()
