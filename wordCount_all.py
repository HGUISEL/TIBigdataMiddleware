from datetime import datetime
import time
import json
import sys
import traceback
import os
import gensim
from gensim import corpora
from gensim.models import TfidfModel

from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

from common import prs
from common import cmm
import numpy as np 
from operator import itemgetter
from elasticsearch import Elasticsearch
import topic_analysis.esAccount as esAcc 

if os.name == "nt":# 윈도우 운영체제
    from eunjeon import Mecab
else:# 현재 리눅스 서버 및 맥은 konlpy으로 미캡 모듈 import
    from konlpy.tag import Mecab

es = Elasticsearch(
        [esAcc.host],
        http_auth=(esAcc.id, esAcc.password),
        scheme="https",
        port= esAcc.port,
        verify_certs=False
)
index = esAcc.index
    

DIR_HomeGraph = "./tfidfHomeGraphdata.json"
DIR_EntireTfidf = "./tfidfs/tfidfTotaldata"  


def makeCorpus (resp):
    corpus = []
    for oneDoc in resp['hits']['hits']:
            # print(len(oneDoc["_source"]["hash_key"]))
            # print(oneDoc["_source"]["hash_key"])
            # print(oneDoc["_source"].keys())

            # file_extracted_content는 글에 있는 첨부파일
            # post_body는 글의 본문
            if "file_extracted_content" in oneDoc["_source"].keys() and "post_body" in oneDoc["_source"].keys():
                corpus.append(
                    {
                        "hash_key" : oneDoc["_source"]["hash_key"],
                        "post_title" : oneDoc["_source"]["post_title"],
                        "content" : oneDoc["_source"]["post_body"] + oneDoc["_source"]["file_extracted_content"]
                    }
                )
            elif "file_extracted_content" in oneDoc["_source"].keys():
                corpus.append(
                    {
                        "hash_key" : oneDoc["_source"]["hash_key"],
                        "post_title" : oneDoc["_source"]["post_title"],
                        "content" : oneDoc["_source"]["file_extracted_content"]
                        }
                    )

            elif "post_body" in oneDoc["_source"].keys():
                corpus.append(
                    {
                        "hash_key" : oneDoc["_source"]["hash_key"],
                        "post_title" : oneDoc["_source"]["post_title"],
                        "content" : oneDoc["_source"]["post_body"]
                        }
                    )
    # print(len(corpus[0]["content"]))
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
    # print(len(corpus["contents"][0])) # 첫번째 문서의 단어개수 확인

    # Tokenize documents
    print("Tokenize Data")
    (hash_key, titles, tokenized_doc, contents) = dataPrePrcs(corpus)
    # print(len(tokenized_doc[0])) # 전처리 끝난 단어들 확인

    # Vectorize documents
    print("Vectorize Data")
    vectorizer = CountVectorizer(analyzer='word', max_features=int(100), tokenizer=None)

    # Analyze documents
    count_result = []
    for tokenList in tokenized_doc:
        if len(tokenList) > 0 :
            
            words=vectorizer.fit(tokenList)
 
            words_fit = vectorizer.fit_transform(tokenList)

            word_list=vectorizer.get_feature_names() 
            count_list = words_fit.toarray().sum(axis=0)


            df=pd.DataFrame()
            df["words"] = word_list
            df["count"] = count_list

            count_list = list([int(x) for x in count_list])
            df = df.sort_values(by=['count'], axis=0, ascending=False)
            #dict_words = dict(zip(word_list,count_list))
            dict_words = df.set_index('words').T.to_dict('records') #type: list
            dict_words = dict_words[0]

            list_count = list()

            for key, value in dict_words.items():
                wordCountList = [key,value]
                list_count.append(wordCountList)
        else:
            list_count = []
        count_result.append(list_count)
    
    # Create result 
    print("Create Result Object")
    result = []
    if len(hash_key) == len(titles) == len(count_result):
        print("analysis succesfully completed")
        print("hash길이:",len(hash_key), " title길이:", len(titles), " result길이:", len(count_result))
    else:
        raise Exception("분석에 빠진 문서가 있습니다. \n" + "hash길이" +len(hash_key)+ "title길이" + len(titles) + "result길이" + len(count_result) )
    for i in range(len(count_result)):
        result.append({"hash_key": hash_key[i], "docTitle": titles[i], "count": count_result[i]})
    return result

def createJson(result, count):
    # Save into Json format
    with open("{dir}{num}.json".format(dir=DIR_EntireTfidf, num=count), 'w', -1, "utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

import account.MongoAccount as monAcc
from pymongo import MongoClient

def saveDataMongodb(result, reset = False):
    client = MongoClient(monAcc.host, monAcc.port)
    db=client.analysis
    #전체삭제
    if reset:
        db.counts.delete_many({})
    #저장
    db.counts.insert_many(result)



# 2021.01.07 YHJ
def getAllCountTable(hash_key = False):
    # if there's target hashkey, don't reset mongodb and search the target data from es
    # if want to get all, reset mongodb and search all data from es
    if hash_key:
        resetMongo = False
        getAll = False
    else:
        resetMongo = True
        getAll = True

    if getAll:
        count = 0
        # Get first 100 data
        resp = es.search( 
            index = index, 
            body = { "size":100, "query": { "match_all" : {} } },    
            scroll='10m'
        )
        # Save Scroll id for next search
        scrollId = resp["_scroll_id"]

        analysisResult = runAnalysis(resp)
        # json 형식으로 저장하기
        # createJson(analysisResult, count)
        
        # mongodb에 저장하기.
        saveDataMongodb(analysisResult, reset = resetMongo)

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
            # json 형식으로 저장하기
            # createJson(analysisResult, count)

            # mongodb에 저장하기
            saveDataMongodb(analysisResult)
            

            print("done with #{}".format(count))
            cmm.showTime()

    else:
        hash_key_list = []
        hash_key_list.append(hash_key)
        resp = es.search( 
            index = index, 
            body = { "size":100,
                "query":{
                    "bool":{
                        "filter":{
                            'terms':{'hash_key':hash_key_list}
                        }
                    }
                }
            }
        )
        analysisResult = runAnalysis(resp)
        print("Analysis complete")
        # json 형식으로 저장하기
        # createJson(analysisResult, count)
        
        # mongodb에 저장하기.
        saveDataMongodb(analysisResult, reset = resetMongo)
        return analysisResult

if __name__ == "__main__":
    # print(getAllTfidfTable("10134412237507850583"))
    getAllCountTable()