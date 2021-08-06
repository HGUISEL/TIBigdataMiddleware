from datetime import datetime
import time
import json
import sys
import traceback
import os
import gensim
from gensim import corpora
from gensim.models import TfidfModel
from common import prs
from common import cmm
import numpy as np 
from operator import itemgetter
from elasticsearch import Elasticsearch

if os.name == "nt":# 윈도우 운영체제
    from eunjeon import Mecab
else:# 현재 리눅스 서버 및 맥은 konlpy으로 미캡 모듈 import
    from konlpy.tag import Mecab
ESindex = 'nkdb_new_210526'
es = Elasticsearch(hosts='https://kubic-repo.handong.edu:19200',http_auth=( 'elastic','2021HandongEPP!NTH201#!#!'),verify_certs=False)    
    

DIR_HomeGraph = "./tfidfHomeGraphdata.json"
DIR_EntireTfidf = "./tfidfs/tfidfTotaldata"  


def makeCorpus (resp):
    corpus = []
    for oneDoc in resp['hits']['hits']:
            #print(len(oneDoc["_source"]["hash_key"]))
            #print(oneDoc["_source"]["hash_key"])
            if "file_extracted_content" in oneDoc["_source"].keys():
                corpus.append(
                    {
                        "hash_key" : oneDoc["_source"]["hash_key"],
                        "post_title" : oneDoc["_source"]["post_title"],
                        "content" : oneDoc["_source"]["file_extracted_content"]
                    }
                )
            elif "hash_key" in oneDoc["_source"].keys():
                corpus.append(
                    {
                        "hash_key" : oneDoc["_source"]["hash_key"],
                        "post_title" : oneDoc["_source"]["post_title"],
                        "content" : oneDoc["_source"]["post_body"]
                        }
                    )
    return corpus

def filterEmptyDoc (corpus):
    hash_key = []
    titles = []
    contents = []

    for idx, doc in enumerate(corpus):
        if doc["content"] != "":
            hash_key.append(doc["hash_key"])
            titles.append(doc["post_title"])
            contents.append(doc["content"])
    
    return {"hash_key" : hash_key, "titles" : titles, "contents" : contents}

def dataPrePrcs(corpus):
    cnt = 0
    hashList = corpus["hash_key"]
    titles = corpus["titles"]
    contents = corpus["contents"]
    import re
    rex1 = re.compile('[^가-힣0-9*.?,!]')#한글 숫자 자주 쓰는 문자만 취급
    
    tagger = Mecab()
    for i,c in enumerate(contents):
        try:
            c = rex1.sub(" ",c)
        except Exception:
            # print("에러 : title : ", titles[i], ", content : ", c)# 문서 내용이 None
            cnt = cnt+1
            # print(cnt)
    
    num_co = 0
    tokenized_doc = []
    failIdxList = []
    
    for i, c in enumerate(contents):
        num_co = num_co + 1
        try:
            t = tagger.nouns(c)
            tokenized_doc.append(t)
        except:
            failIdxList.append(i)
    for idx in reversed(failIdxList):
        hashList.pop(idx)
        titles.pop(idx)


    # 한글자 단어들 지우기!
    num_doc = len(tokenized_doc)
    for i in range(num_doc):
        tokenized_doc[i] = [word for word in tokenized_doc[i] if len(word) > 1]
    
    return hashList, titles, tokenized_doc, contents


def runAnalysis(resp):
    # Create corpus object
    print("Create corpus")
    corpus = makeCorpus(resp)
    
    # Take only non-empty data
    print("Filter Empty Data")
    corpus = filterEmptyDoc(corpus) 

    # Tokenize documents
    print("Tokenize Data")
    (hash_key, titles, tokenized_doc, contents) = dataPrePrcs(corpus)

    # Dictionarize documents
    print("Dictionarize Data")
    dictionarizedDoc = corpora.Dictionary(tokenized_doc)

    # Tfidif Modeling
    print("Modeling Data")
    corpus = corpus = [dictionarizedDoc.doc2bow(line) for line in tokenized_doc]
    tfidfModel = TfidfModel(corpus)

    sortedWords = []
    # Sort by tfidf value
    for id, word_list in enumerate(tfidfModel[corpus]):
        word_list = sorted(word_list, key=itemgetter(1), reverse = True) 
        sortedWords.append((id, word_list))
    print("Sort Data: ")

    # Create Object of tfidf
    print("Create Result Object")
    result = []
    for i, wordValuePair in sortedWords:
        wordValuePair = sortedWords[i]
        tfidfWord = []
        for idx, (wordId, tfidfValue) in enumerate(wordValuePair[1]):
            tfidfWord.append((dictionarizedDoc[wordId], tfidfValue))
        result.append({"hash_key": hash_key[i], "docTitle": titles[i], "tfidf": tfidfWord})

    return result

def createJson(result, count):
    # Save into Json format
    with open("{dir}{num}.json".format(dir=DIR_EntireTfidf, num=count), 'w', -1, "utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

# 2021.01.07 YHJ
def getAllTfidfTable():
    count = 0
    # Get first 100 data
    resp = es.search( 
        index = ESindex, 
        body = { "size":100, "query": { "match_all" : {} } },    
        scroll='10m'
    )

    # Save Scroll id for next search
    scrollId = resp["_scroll_id"]

    analysisResult = runAnalysis(resp)
    createJson(analysisResult, count)

    print("Done with the first set")
    cmm.showTime()
    
    while len(resp['hits']['hits']):
        count = count + 1
        print("start set #{}".format(count))
        resp = es.scroll( 
            scroll_id = scrollId, 
            scroll='10m'
            )        
        analysisResult = runAnalysis(resp)
        createJson(analysisResult, count)
        print("done with #{}".format(count))
        cmm.showTime()

if __name__ == "__main__":
    getAllTfidfTable()    
