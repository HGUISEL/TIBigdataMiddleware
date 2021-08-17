from sklearn.feature_extraction.text import TfidfVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.exceptions import NotFittedError

import pymongo
from pymongo import MongoClient

import pandas as pd
import numpy as np
import json
import os
import h5py
import csv
import schedule
import time
import os.path
import traceback
import pickle
import joblib
import sys
import logging
from topic_analysis.Pre_date import *
from topic_analysis.Post_date import *
from topic_analysis.__get_logger import __get_logger
import topic_analysis.MongoAccount as MongoAccount

## 필요 파일, dir 만들어 주는 코드 ###

def make_dir():
    log_path='./log'
    model_path='./model'
    svm_log='./log/multi_svm.log'
    svm_train='./log/multi_svm_train.log'
    log_error='./log/multi_svm_error.log'
    train_data='./train_data'


    if not os.path.exists(log_path):
        os.mkdir(log_path)
        logger.info("multi_svm의 log를 저장할./log 디렉토리를 생성하였습니다.")
        if not os.path.exists(log_error):
            os.touch(log_error)
            logger.info("multi_svm의 error를 저장할./log/multi_svm_error.log파일을 생성하였습니다.")
        elif not os.path.exists(svm_log):
            os.touch(svm_log)
            logger.info("multi_svm을 사용한 주제예측을 시행일자가 저장될 ./log/multi_svm.log파일이 생성하었습니다.")
        elif not os.path.exists(svm_train):
            os.touch(svm_train)
            logger.info("multi_svm 모델훈련 시행일자가 저장될 ./log/multi_svm_train.log파일을 생성하였습니다")
    elif not os.path.exists(model_path):
        os.mkdir(model_path)
        logger.info("multi_svm model을 저장할 ./model 디렉토리를 생성하였습니다.")
    elif not os.path.exists(train_data):
        os.mkdir(train_data)
        logger.info("multi_svm 모델 train data가 저장될 ./train_data 디렉토리를 생성하였습니다.")


def SVMTrain():
    import time
    import numpy as np
    print('train data를 불러옵니다.')
    tvc=TfidfVectorizer()

    ##### 모델링 ######
    #train data load
    data=pd.read_csv("./train_data/multi_20110224-2021024.csv")
    
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

    filename='./model/multi_SVM.h5'
    dataname='./model/multi_tvc.pickle'
    
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
    filename='./model/multi_SVM_final.h5'
    dataname='./model/multi_tvc_final.pickle'
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

def MoEs(date):
    #Mongo
    client=MongoClient(
        host=MongoAccount.host, 
        port=MongoAccount.port)
    logger.info('MongoDB에 연결을 성공했습니다.')
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

