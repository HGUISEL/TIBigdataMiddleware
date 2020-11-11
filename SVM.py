import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
import pickle
from sklearn.pipeline import Pipeline
#from keras.models import load_model
#from sklearn.externals import joblib
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
import joblib
import pymongo
from pymongo import MongoClient
import json
from common.cmm import showTime, SAMP_DATA_DIR
from common import prs
import os
import h5py
import csv

def make_SVM():
    data=pd.read_csv("/home/dapi2/TIBigdataMiddleware/train data (svm)/topic_20100909-20200909.csv")
    data.columns.to_list()
    data = data.drop_duplicates()
    del data['Unnamed: 0']
    """
    svm = Pipeline([('vect', CountVectorizer()),#'어떤 함수인지 표기'#있을때, 없을때 표로.. 차이가 없으면 리포트./왜 이게 필요한지/
                         ('tfidf', TfidfTransformer()),#tfidf(특정 단어가 특정문서에서 얼마나 중요한지 가중치를 나타내주는 계산법)
                                                       # tfidf로 count matrix를 정규화시킨다. 
                         ('clf-svm', SGDClassifier(loss='hinge', penalty='l2', alpha=0.00001, random_state=42,n_iter_no_change=5))])
    
    #SGDClassifier: SVM은 linear classifiers을 적용한것(SVM, logistic regression등 의 모델에서 사용되는 함수
    #: loss='hinge'-->SVM(default값)
    #penalty: 정규화 표준 l2/ 
    #alpha: 정규화 항을 곱하는 상수, 값이 클수록 정규화가 더 강해진다. 
    svm_model = svm.fit(data, topic)
    joblib.dump(svm_model,'/home/dapi2/TIBigdataMiddleware/model/SVM.h5')
    #model.save('/home/dapi2/TIBigdataMiddleware/model/SVM.h5')
    """
    tvc=TfidfVectorizer()
    tvc_data=tvc.fit_transform(data["키워드"])

    svm_model=SGDClassifier(loss='hinge', penalty='l2', alpha=0.00001, random_state=42,n_iter_no_change=5)
    svm_model= svm_model.fit(tvc_data, data['주제'])
    pickle.dump(svm_model,open("/home/dapi2/TIBigdataMiddleware/model/svm.h5",'wb'))
    
    return svm_model

global model

def SVM(ndoc):
    # Phase 1 : READY DATA
    print("\n\n##########Phase 1 : READY DATA##########")
    (doc_id, titles, tokenized_doc, contents) = prs.readyData(ndoc, True)

    # Phase 2 : Load Model
    print("\n\n##########Phase 2 : Load Model##########")
    if (os.path.isfile("/home/dapi2/TIBigdataMiddleware/model/svm.h5")==False):
        svm_model=make_SVM()
    else:
        svm_model=joblib.load('/home/dapi2/TIBigdataMiddleware/model/svm.h5')
        #svm_model=pickle.load(open('/home/dapi2/TIBigdataMiddleware/model/svm.h5','rb'))
    
    tvc=TfidfVectorizer()
    for i in range(len(tokenized_doc)):
        corpus=(tvc.transform(text[i]))
        result.append((corpus[i], list(model.predict(corpuds))[0]))
    
    #result=svm_model.predict(tokenized_doc)

    #corpus = [tvc.fit_transform(text) for text in tokenized_doc]
    #result= svm_model.predict(corpus)
    #print(len(corpus))

    #for i in range(len(corpus)):
    #    result=svm_model.predict(corpus[i])
    #result = svm_model.predict(corpus)
    
    print(result)
    #id2word = corpora.Dictionary(tokenized_doc)#문서 별 각 단어에 고유 id 부여 : 문서를 벡터화
    #tokenized_doc=pd.DataFrame(tokenized_doc)
    #result = [svm_model.predict(text) for text in range (len(tokenized_doc))]
    #print(tokenized_doc)
    #result=svm_model.predict(tokenized_doc)
    #print(result)
        
    #result=[svm_model.predict(tokenized_doc[cnt]) for cnt in range(len(tokenized_doc))]
    

    return result
    """
    svm_model=joblib.load('/home/dapi2/TIBigdataMiddleware/model/SVM.h5')

    #result= [svm_model.predict(text) for text in tokenized_doc]
    
    print(tokenized_doc[0])

    #result= svm_model.predict(tokenized_doc)
    result=[]
    for i in range(len(tokenized_doc)):
        result.append(svm_model.predict(tokenized_doc[i])) 
    
    #model= SGDClassifier(loss='hinge', penalty='l2', alpha=0.00001, random_state=42,n_iter_no_change=5)
    
    #svm_model = model.fit(tvc, NUM_TOPICS)
    
    print(result)

    return result
    """
    