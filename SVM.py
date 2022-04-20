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

### 필요 파일, dir 만들어 주는 코드 ###
def make_dir():
     
    log_path='./log'
    model_path='./model'
    svm_log='./log/svm.log'
    svm_train='./log/svm_train.log'
    log_error='./log/svm_error.log'
    train_data='./train_data'


    if not os.path.exists(log_path):
        os.mkdir(log_path)
        logger.info("svm의 log를 저장할./log 디렉토리를 생성하였습니다.")
        if not os.path.exists(log_error):
            os.touch(log_error)
            logger.info("svm의 error를 저장할./log/svm_error.log파일을 생성하였습니다.")
        if not os.path.exists(svm_log):
            os.touch(svm_log)
            logger.info("svm을 사용한 주제예측을 시행일자가 저장될 ./log/svm.log파일이 생성하었습니다.")
        if not os.path.exists(svm_train):
            os.touch(svm_train)
            logger.info("svm 모델훈련 시행일자가 저장될 ./log/svm_train.log파일을 생성하였습니다")
    if not os.path.exists(model_path):
        os.mkdir(model_path)
        logger.info("svm model을 저장할 ./model 디렉토리를 생성하였습니다.")
    if not os.path.exists(train_data):
        os.mkdir(train_data)
        logger.info("svm 모델 train data가 저장될 ./train_data 디렉토리를 생성하였습니다.")


##### SVM 모델을 훈련시키는 함수 #####
def SVMTrain():
    logger=__get_logger()
    make_dir()

    import time
    #f.write("train data를 불러옵니다")
    tvc=TfidfVectorizer()
    
    ### train_data 불러오기 ###
    try:
        logger.info("훈련할 데이터를 불러옵니다.")
        data=pd.read_csv("/home/middleware/train_data/single_20110224-20210224.csv", engine='python', error_bad_lines=False)
        logger.info("훈련할 csv파일을 가져왔습니다.")
        data.columns.to_list()
        data = data.drop_duplicates()
        del data['Unnamed: 0']
        logger.info('train data를 불러오는데 성공하였습니다.')
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)#+"\n"+ str(trace_back)
        logger.error('train data를 불러오는데 실패하였습니다. %s',message)
        #sys.exit()

    ### 키워드 데이터의 가중치 구하는 함수 ###
    try:
        logger.info('키워드 데이터의 가중치를 구합니다.')
        start=time.time()
        tvc_data=tvc.fit_transform(data["키워드"])
        logger.info('키워드 데이터의 가중치를 구하는데 성공하였습니다.')
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)#+"\n"+ str(trace_back)
        logger.error('가중치를 구하는데 실패하였습니다. %s',message)
        #sys.exit()

    ### SVM 모델 학습 ###
    try:
        logger.info('SVM 모델학습을 시작합니다.')
        svm_model=SGDClassifier(loss='hinge', penalty='l2', alpha=0.00001, random_state=42,n_iter_no_change=5)
        logger.info(set(data['주제']), "의 주제로 학습을 진행합니다" )
        model= svm_model.fit(tvc_data, data['주제'])
        logger.info('SVM 모델학습을 완료하였습니다.')
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)#+"\n"+ str(trace_back)
        logger.error('SVM 모델학습에 실패하였습니다. %s',message)
        #sys.exit()

    ### SVM 모델 저장###
    try:
        filename='./model/SVM.h5'
        dataname='./model/tvc.pickle'

        with open(filename, 'wb') as filehandle:
            pickle.dump(model,filehandle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(dataname, 'wb') as datahandle:
            pickle.dump(tvc,datahandle, protocol=pickle.HIGHEST_PROTOCOL)
        TT=time.time()-start
        logger.info("훈련한 모델을 저장하였습니다.")
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)#+"\n"+ str(trace_back)
        logger.error('SVM모델저장에 실패하였습니다. %s',message)
        #sys.exit()

    return "SVM훈련과정을 종료하였습니다."

##### SVM으로 주제 예측해주는 함수 #####
def SVMTest(tokenized_doc):
    logger=__get_logger()

    ### 저장된 모델을 읽어오기 ###
    try:
        logger.info("저장된 모델을 불러옵니다. ")
        filename='./model/SVM.h5'
        dataname='./model/tvc.pickle'
        
        with open(filename, 'rb') as filehandle:
            model = pickle.load(filehandle)
            logger.info(model)
        with open(dataname, 'rb') as datahandle:
            tvc = pickle.load(datahandle)
            logger.info(tvc)
        logger.info("저장된 모델을 불러오는 데 성공했습니다. ")
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)#+"\n"+ str(trace_back)
        logger.error('SVM 모델 불러오기에 실패하였습니다. %s',message)
        #sys.exit()
    
    ###주제예측 시작하기###
    try:
        logger.info("주제예측을 시작합니다.")

        result=list()
        #북한데이터 tokenizer & predict
        for i in range(len(tokenized_doc)):
            if(len(tokenized_doc[i])>0):
                tvc_lst=(tvc.transform(tokenized_doc[i]))#tfidfvectorizer
                result.append(list(model.predict(tvc_lst))[0])#predict
            else:
                result.append("")#predict
        logger.info(len(result),"개의 데이터의 주제예측을 성공적으로 완료하였습니다.")
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)#+"\n"+ str(trace_back)
        logger.error('SVM를 사용한 주제예측에 실패하였습니다. %s',message)
        #sys.exit()
    return result

def MoEs(date):
    logger=__get_logger()
    ### 필요한 디렉토리, 파일 만들어주는 함수호출 ###
    make_dir()
    
    ### MongoDB를 연결 및 삽입해하기 ###
    try:    
        logger.info("MongoDB에 연결을 시도합니다.")
        client=MongoClient(
            host=MongoAccount.host, 
            port=MongoAccount.port)
        logger.info('MongoDB에 연결을 성공했습니다.')
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)#+"\n"+ str(trace_back)
        logger.error('MongoDB연결에 실패하였습니다. %s',message)
        #sys.exit()

    ### db상황에 따라 SVM 실행하기 ###
    try:
        db=client.analysis
        db.topics.delete_many({})# 전체 초기화
        collection_num=db.topics.count()
        if collection_num==0:#최초 시작
            logger.info('svmDB에 ',collection_num,'개의 데이터가 있습니다. ')
            (hash_key, doc_title, tokenized_doc, contents, times)=Pre_date(date)
            logger.info('MongoDB의 ', date, '이전의 데이터의 주제를 분석합니다.')
            result=SVMTest(tokenized_doc)
        else: 
            logger.info('svmDB에 ',collection_num,'개의 데이터가 있습니다. ')
            (hash_key, doc_title, tokenized_doc, contents, times)=Post_date(date)
            logger.info('MongoDB에 새로유입된 ',len(tokenized_doc),'개의 데이터의 주제를 분석합니다.')
            result=SVMTest(tokenized_doc)#갱신  
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)+"\n"+ str(trace_back)
        logger.error('SVM을 통해 주제예측한 데이터 저장에 실패하였습니다. %s',message)
        #sys.exit()
    
    ### db의 svm collection에 데이터 삽입하기 ###
    try:
        logger.info('MongoDB의 svm collection에 분석한 데이터의 주제를 저장을 시작합니다.')
        for i in range(len(hash_key)):
            doc={
                "hash_key" : hash_key[i],
                "doc_title" : doc_title[i],
                "topic" : result[i],
                "timestamp": times[i]
            }
            db.topics.insert_one(doc)
        logger.info('MongoDB의 svm collection에 분석한 데이터를 저장을 완료했습니다.')
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)#+"\n"+ str(trace_back)
        logger.error('MongoDB의 svm collection에 분석한 데이터를 저장하는데 실패했습니다. %s',message)
        #sys.exit()
    return result

