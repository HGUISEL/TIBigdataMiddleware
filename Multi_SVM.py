import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.exceptions import NotFittedError
import pickle
import joblib
import pymongo
from pymongo import MongoClient
import json
from common.cmm import showTime, SAMP_DATA_DIR
from common import prs
import os
import h5py
import csv
from elasticsearch import Elasticsearch
import schedule
import time
import os.path
import traceback
import sys
import esFunc
import re
import schedule
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from konlpy.tag import Komoran

if os.name == "nt":# 윈도우 운영체제
    from eunjeon import Mecab
else:# 현재 리눅스 서버 및 맥은 konlpy으로 미캡 모듈 import
    from konlpy.tag import Mecab

#### 토큰화해주는 함수 ####
def dataPrePrcs(contents):
    no_kor_num=0
    tagger = Mecab()
    print(len(contents))
    print('mecab 형태소 분석기를 실행합니다.')
    #f.write("Mecab을 실행합니다.")

    print('한글 외의 글자를 삭제합니다.')
    #f.write("한글 외의 글자를 삭제합니다.")
    hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')
    for j in range(len(contents)):
        if re.match('[^ ㄱ-ㅣ가-힣]+',str(contents[j])):
            no_kor_num+=1
    contents = [hangul.sub('',str(contents[cn])) for cn in range(len(contents))]
    print('한글 외의 글자를 가진',no_kor_num,'개의 문서 삭제를 완료했습니다.')

    #f.write("한글 외의 글자 삭제를 완료했습니다.")

    print('각 문서의 명사를 추출합니다.')
    #f.write("각 문서의 명사를 추출합니다.")
    #from tqdm import tqdm_notebook
    from tqdm import tqdm
    tokenized_doc = []
    for cnt in tqdm(range(len(contents))):
        #print(cnt, '번 문서의 명사를 추출합니다.')
        nouns = tagger.nouns(contents[cnt])
        #print(len(nouns), '토큰들을 통합합니다.')
        tokenized_doc.append(nouns)
    #print('각 문서의 명사를', len(nouns),'개 추출을 완료했습니다.')
    #f.write("각 문서의 명사를 추출을 완료했습니다.")

    # 한글자 단어들 지우기!
    print('한 글자 단어를 삭제합니다.')
    #f.write("한 글자 단어를 삭제합니다.")
    num_doc = len(tokenized_doc)
    one_word=0

    for i in range(num_doc):
        tokenized_doc[i] = [word for word in tokenized_doc[i] if len(word) > 1]

    #print('한 글자 단어 ', one_word ,'개를 삭제를 완료했습니다.')
    print("한 글자 단어를 삭제를 완료했습니다.")
    #f.write("한 글자 단어를 삭제를 완료했습니다.")
    return tokenized_doc

def SVMTrain():
    import time
    import numpy as np
    print('train data를 불러옵니다.')
    tvc=TfidfVectorizer()

    ##### 모델링 ######
    #train data load
    data=pd.read_csv("./train_data/multi_20110224-2021022.csv")
    
    data.columns.to_list()
    data = data.drop_duplicates()
    del data['Unnamed: 0']
    print('train data를 불러오는데 성공하였습니다.')

    print('키워드 데이터의 가중치를 구합니다.')
    start=time.time()
    tvc_train=tvc.fit_transform(data["키워드"])
    print('키워드 데이터의 가중치를 구하는데 성공하였습니다.')

    #SVM모델 구축 및 학습
    svm_model=SGDClassifier(loss='hinge', penalty='l2', alpha=0.00001, random_state=42,n_iter_no_change=5)
    model= svm_model.fit(tvc_train, data["주제"])

    filename='model/multi_SVM.h5'
    dataname='model/multi_tvc.pickle'
    
    with open(filename, 'wb') as filehandle:
        pickle.dump(model,filehandle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(dataname, 'wb') as datahandle:
        pickle.dump(tvc,datahandle, protocol=pickle.HIGHEST_PROTOCOL)
    TT=time.time()-start   
    print(TT,"시간 만에 모델훈련을 완료하였습니다.")
    print("훈련한 모델을 저장하였습니다.")

    return "훈련한 모델을 저장하였습니다."

def SVMTest(tokenized_doc):#북한데이터에 saved model 적용 
    print("저장된 모델을 불러옵니다. ")
    #f.write("저장된 모델을 불러옵니다.")
    filename='model/multi_SVM_final.h5'
    dataname='model/multi_tvc_final.pickle'
    # 저장된 모델을 읽어오기
    with open(filename, 'rb') as filehandle:
        model = pickle.load(filehandle)
    with open(dataname, 'rb') as datahandle:
        tvc = pickle.load(datahandle)
    print("저장된 모델을 불러오는 데 성공했습니다. ")
    #f.write("저장된 모델을 불러오는 데 성공했습니다.")

    print("주제예측을 시작합니다.")
    #f.write("주제예측을 시작합니다.")
    result=list()

    #북한데이터 tokenizer & predict
    for i in range(len(tokenized_doc)):
        if(len(tokenized_doc[i])>0):
            tvc_lst=(tvc.transform(tokenized_doc[i]))#tfidfvectorizer
            result.append(list(model.predict(tvc_lst))[0])#predict
        else:
            result.append("")#predict
    
    print(len(result),"개의 데이터의 주제예측을 성공적으로 완료하였습니다.")
    #f.write("주제예측을 성공적으로 완료하였습니다.")
    return result

def Pre_date(date):
    print('Elasticsearch server에 접속을 시도합니다.')
    index = 'nkdb_new_210526'
    es = Elasticsearch(
        hosts='https://kubic-repo.handong.edu:19200',
        http_auth=( 'elastic','2021HandongEPP!NTH201#!#!'),
        #scheme="https",
        #port=19200,
        verify_certs=False
    )    
    print('Elasticsearch server에 성공적으로 접속하였습니다.')
    
    #이전&현재 데이터
    print('Elasticsearch server에 데이터를 요청합니다.')
    print("date2: ", date)
    #f.write('Elasticsearch server에 데이터를 요청합니다.')
    resp=es.search( 
        index=index, 
        body={   
            "size":100,
            "query":{
                "range" :{
                    "timestamp":{
                        #"type":"date",
                        "lte":date,#이하,
                        "format": "yyyy-MM-dd"
                    }
                },
            },
        },    scroll='1s'
    )

    #old_scroll_id = resp["_scroll_id"]
    sid = resp["_scroll_id"]
    fetched =len(resp['hits']['hits'])
    
    print("fetched: ",fetched)
    #fetched =len(resp['hits']['hits'])


    hash_key=[]
    titles=[]
    contents=[]
    times=[]
    tokenized_doc=[]
    corpus=[]
    corpus2=[]
    count=0

    print('0번부터 99번까지 100개의 데이터를 처리합니다.')
    #f.write('0번부터 99번까지 100개의 데이터를 처리합니다.')
    for i in range(fetched):
        if "file_extracted_content" in resp['hits']['hits'][i]["_source"].keys():    
            hash_key.append((resp['hits']['hits'][i]["_source"]["hash_key"])) 
            titles.append((resp['hits']['hits'][i]["_source"]["post_title"]))
            times.append((resp['hits']['hits'][i]["_source"]["timestamp"]))
            contents.append((resp['hits']['hits'][i]["_source"]["file_extracted_content"]))
   
    from os import path
    resp_count = 0
    while len(resp['hits']['hits']):
        resp_count+=1
        print(resp_count*100,'번부터', resp_count*100+99, '번까지 100개의 데이터를 처리합니다.')
        #f.write(resp_count*100,'번부터', resp_count*100+99, '번까지 100개의 데이터를 처리합니다.')
        resp=es.scroll(scroll_id=sid, scroll='1s')
        fetched=len(resp['hits']['hits'])
        for doc in resp['hits']['hits']:
            if "file_extracted_content" in doc["_source"].keys():
                hash_key.append((doc["_source"]["hash_key"])) 
                titles.append((doc["_source"]["post_title"]))
                times.append((doc["_source"]["timestamp"]))    
                contents.append(doc["_source"]["file_extracted_content"])
             
    #형태소 분석기
    print('형태소 분석기를 실행합니다. ')
    #f.write('형태소 분석기를 실행합니다. ')
    tokenized_doc=dataPrePrcs(contents)
    
    print('형태소 분석기를 실행을 완료하였습니다. ')
    #f.write('형태소 분석기를 실행을 완료하였습니다. ')
    return hash_key, titles, tokenized_doc, contents, times

def Post_date(date):
    print('Elasticsearch server에 접속을 시도합니다.')
    index = 'nkdb_new_210526'
    es = Elasticsearch(
        hosts='https://kubic-repo.handong.edu:19200',
        http_auth=( 'elastic','2021HandongEPP!NTH201#!#!'),
        #scheme="https",
        #port=19200,
        verify_certs=False
    )   
    print('Elasticsearch server에 성공적으로 접속하였습니다.')
    #이전&현재 데이터
    print('Elasticsearch server에 데이터를 요청합니다.')
    #f.write('Elasticsearch server에 데이터를 요청합니다.')
    resp=es.search( 
        index=index, 
        body={   
            "size":100,
            "query":{
                "range" :{
                    "timestamp":{
                        "gt":str(date)#이하
                        ,"format" : "yyyy-MM-dd"
                    }
                },
            },
        },    scroll='1s'
    )

    #old_scroll_id = resp["_scroll_id"]
    sid = resp["_scroll_id"]
    fetched =len(resp['hits']['hits'])


    titles=[]
    contents=[]
    times=[]
    hash_key=[]
    tokenized_doc=[]
    corpus=[]
    corpus2=[]
    count=0

    

    print('0번부터 99번까지 100개의 데이터를 처리합니다.')
    #f.write('0번부터 99번까지 100개의 데이터를 처리합니다.')
    for i in range(fetched):
        if "file_extracted_content" in resp['hits']['hits'][i]["_source"].keys():    
            hash_key.append((resp['hits']['hits'][i]["_source"]["hash_key"]))
            titles.append((resp['hits']['hits'][i]["_source"]["post_title"]))
            times.append((resp['hits']['hits'][i]["_source"]["timestamp"]))
            contents.append((resp['hits']['hits'][i]["_source"]["file_extracted_content"]))
   
    from os import path
    resp_count = 0
    while len(resp['hits']['hits']):
        resp_count+=1
        print(resp_count*100,'번부터', resp_count*100+99, '번까지 100개의 데이터를 처리합니다.')
        #f.write(resp_count*100,'번부터', resp_count*100+99, '번까지 100개의 데이터를 처리합니다.')
        resp=es.scroll(scroll_id=sid, scroll='1s')
        fetched=len(resp['hits']['hits'])
        for doc in resp['hits']['hits']:
            if "file_extracted_content" in doc["_source"].keys():
                hash_key.append((doc["_source"]["hash_key"])) 
                titles.append((doc["_source"]["post_title"]))
                times.append((doc["_source"]["timestamp"])) 
                contents.append(doc["_source"]["file_extracted_content"])
             
    #형태소 분석기
    print('형태소 분석기를 실행합니다. ')
    #f.write('형태소 분석기를 실행합니다. ')
    tokenized_doc=dataPrePrcs(contents)    
    print('형태소 분석기를 실행을 완료하였습니다. ')
    #f.write('형태소 분석기를 실행을 완료하였습니다. ')
    return hash_key, titles, tokenized_doc, contents, times

def MoEs(date):
    #Mongo
    client=MongoClient(host='localhost',port=27017)
    print('MongoDB에 연결을 성공했습니다.')
    #f.write("MongoDB에 연결을 성공했습니다..")
    db=client.topic_analysis

    collection_num=db.multi_label_svm.count()
    date=date
    print("\n")
    print(collection_num)
    if collection_num==0:#최초 시작
        print('svmDB에 ',collection_num,'개의 데이터가 있습니다. ')
        (hash_key, doc_title, tokenized_doc, contents, times)=Pre_date(date)
        print('MongoDB의 ', date, '이전의 데이터의 주제를 분석합니다.')
        #f.write("MongoDB의 모든 데이터의 주제를 분석합니다.")
        result=SVMTest(tokenized_doc)
        
    else: 
        print('svmDB에 ',collection_num,'개의 데이터가 있습니다. ')
        (hash_key, doc_title, tokenized_doc, contents, times)=Post_date(date)
        print('MongoDB에 새로유입된 ',len(tokenized_doc),'개의 데이터의 주제를 분석합니다.')
        #f.write("MongoDB에 새로유입된 데이터의 주제를 분석합니다.")
        result=SVMTest(tokenized_doc)#갱신  
    
    print('MongoDB의 svm collection에 분석한', len(result),'개의 주제를 저장합니다.')
    #f.write("MongoDB의 svm collection에 분석한 주제를 저장합니다")
    
    for i in range(len(hash_key)):
        doc={
            "hash_key" : hash_key[i],
            "doc_title" : doc_title[i],
            "topic" : result[i],
            "timestamp": times[i]
        }
        db.multi_label_svm.insert_one(doc)
    showTime()
    print('MongoDB의 svm collection에 분석한', len(result),'개의 주제를 저장을 완료했습니다.')
    #f.write("MongoDB의 svm collection에 분석한 주제를 저장을 완료했습니다")
    return result

