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
import nltk
from nltk.corpus import stopwords

import re

es = Elasticsearch(
        [esAcc.host],
        http_auth=(esAcc.id, esAcc.password),
        scheme="https",
        port= esAcc.port,
        verify_certs=False
)
index = esAcc.indexPaper
    

DIR_HomeGraph = "./tfidfHomeGraphdata.json"
DIR_EntireTfidf = "./tfidfs/tfidfTotaldata"

def is_english(title):
    hangul = re.compile('[ㄱ-ㅣ가-힣]')
    return title == hangul.sub("",title)

def makeCorpus (resp):
    corpus = []
    for oneDoc in resp['hits']['hits']:
            # print(len(oneDoc["_source"]["hash_key"]))
            # print(oneDoc["_source"]["hash_key"])
            # print(oneDoc["_source"].keys())

            # file_extracted_content는 글에 있는 첨부파일
            # post_body는 글의 본문
            if "file_extracted_content" in oneDoc["_source"].keys() and "post_body" in oneDoc["_source"].keys():
                postBody = oneDoc["_source"]["post_body"]
                fileExt = oneDoc["_source"]["file_extracted_content"]
                if postBody == None:
                    postBody = ""
                if fileExt == None:
                    fileExt = ""

                oneDoc["_source"]["file_extracted_content"] == None
                corpus.append(
                    {
                        "hash_key" : oneDoc["_source"]["hash_key"],
                        "post_title" : oneDoc["_source"]["post_title"],
                        "content" : postBody + fileExt
                    }
                )
            elif "file_extracted_content" in oneDoc["_source"].keys():
                fileExt = oneDoc["_source"]["file_extracted_content"]
                if fileExt == None:
                    fileExt = ""
                corpus.append(
                    {
                        "hash_key" : oneDoc["_source"]["hash_key"],
                        "post_title" : oneDoc["_source"]["post_title"],
                        "content" : fileExt
                        }
                    )

            elif "post_body" in oneDoc["_source"].keys():
                postBody = oneDoc["_source"]["post_body"]
                if postBody == None:
                    postBody = ""
                corpus.append(
                    {
                        "hash_key" : oneDoc["_source"]["hash_key"],
                        "post_title" : oneDoc["_source"]["post_title"],
                        "content" : postBody
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
    rex1 = re.compile('[^가-힣0-9a-zA-Z*.?,!]')#한글 숫자 영어 자주 쓰는 문자 취급

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
    
    #tag가 startswith("n")이거나 태그가 숫자, 영어, 한문 일 경우 살리도록.
    tagger = Mecab()

    indx = 0
    for i, c in enumerate(contents):
        num_co = num_co + 1
        if is_english(titles[indx]):
            # if hashList[indx] == "883894918290590972":
            #     print('883894918290590972 문서가 영어모드로 분석되었습니다.')
            lan = "EN"
            tagList = ["NN", "NNS", "NNP", "NNPS", "FW"]
        else:
            # if hashList[indx] == "883894918290590972":
            #     print('883894918290590972 문서가 한글모드로 분석되었습니다.')
            lan = "KR"
            tagList = ["NNG", "NNP", "NNB", "NNBC", "NR", "NP", "SL", "SH", "SN"]
        try:
            if lan == "KR":
                t = tagger.pos(c)
            if lan == "EN":
                words = nltk.word_tokenize(c)
                t = nltk.pos_tag(words)
                
            token_list = []
            # [(word,tag),(word,tag)] 
            # 영어의 경우 stopwords 분석 추가
            for word, tag in t:
                if tag in tagList:
                    if lan == "EN":
                        # stops = set(stopwords.words('english'))
                        # if word not in stops:
                            # token_list.append(word)
                        token_list.append(word)
                    else:
                        token_list.append(word)
            tokenized_doc.append(token_list)
         
        except:
            failIdxList.append(i)
        # print(indx)
        indx += 1  

    for idx in reversed(failIdxList):
        hashList.pop(idx)
        titles.pop(idx)


    # 한글자 단어들 지우기!
    num_doc = len(tokenized_doc)
    for i in range(num_doc):
        tokenized_doc[i] = [word for word in tokenized_doc[i] if len(word) > 1]

    # 원문과 WC result 파일로 저장하기
    # text_file = open("text.txt", "w")
    # text_file.write(contents[0])
    # text_file.close()
    # resultDict = {"hashList":hashList, "titles":titles, "tokenized_doc":tokenized_doc}
    # df = pd.DataFrame(resultDict)
    # df.to_csv("wcPrsResult.csv")
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
    # analyzer: 분석단위, max_features: 최대 개수(output단어 개수), 
    # tokenizer: 토큰화할 함수, ngram_range: 분석할 ngram 범위(1,2) --> unigram 이랑 bigram둘다 셈!
    vectorizer = CountVectorizer(analyzer='word', max_features=int(100), tokenizer=None, ngram_range = (1,2))
    # vectorizer = CountVectorizer(analyzer='word', max_features=int(100), tokenizer=None)
    # vectorizer = CountVectorizer(analyzer=lambda x:x, max_features=int(100), tokenizer=None)

    # Analyze documents
    count_result = []
    for tokenList in tokenized_doc:
        if len(tokenList) > 0 :
            # print(tokenList[0:10])
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
        raise Exception("분석에 빠진 문서가 있습니다. \n" + "hash길이", len(hash_key), "title길이", len(titles), "result길이", len(count_result) )
    for i in range(len(count_result)):
        result.append({"hash_key": hash_key[i], "docTitle": titles[i], "count": count_result[i]})
    return result

def createJson(result, count):
    # Save into Json format
    with open("{dir}{num}.json".format(dir=DIR_EntireTfidf, num=count), 'w', -1, "utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

import account.MongoAccount as monAcc
from pymongo import MongoClient

def saveDataMongodb(result, reset = False, test = False):
    client = MongoClient(monAcc.host, monAcc.port)
    if test:
        # 테스트용
        db=client.topic_analysis
    else:
        # 서버
        db=client.analysis

    #전체삭제
    if reset:
        db.counts.delete_many({})
    #저장
    id = db.counts.insert_many(result)
    print(id.acknowledged)



# 2021.01.07 YHJ
# hash_key 있으면 Mongo reset안함
# isTest 가 True면 테스트에 저장함.
def getAllCountTable(hash_key = False, isTest = False):
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
        saveDataMongodb(analysisResult, reset = resetMongo, test = isTest)

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
            saveDataMongodb(analysisResult, test = isTest)
            

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
        saveDataMongodb(analysisResult, reset = resetMongo, test = isTest)
        return analysisResult

if __name__ == "__main__":
    # print(getAllCountTable("883894918290590972", isTest = True))
    getAllCountTable()