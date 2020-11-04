import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
#from sklearn.externals import joblib
import joblib
import pymongo
from pymongo import MongoClient
import json
from common.cmm import showTime, SAMP_DATA_DIR
from common import prs
# 중복데이터 제거
#data = data.drop_duplicates()

# 모델 생성
"""
text_clf_svm = Pipeline([('vect', CountVectorizer()),#'어떤 함수인지 표기'#있을때, 없을때 표로.. 차이가 없으면 리포트./왜 이게 필요한지/
                         ('tfidf', TfidfTransformer()),#tfidf(특정 단어가 특정문서에서 얼마나 중요한지 가중치를 나타내주는 계산법)
                                                       # tfidf로 count matrix를 정규화시킨다. 
                         ('clf-svm', SGDClassifier(loss='hinge', penalty='l2', alpha=0.00001, random_state=42,n_iter_no_change=5))])

#모델 학습
text_clf_svm = text_clf_svm.fit(train["키워드"], train["주제"])

#파이프라인 저장
joblib.dump(text_clf_svm,'/home/dapi2/TIBigdataMiddleware/SVM.h5')
"""

def model(ndoc):
    # Phase 1 : READY DATA
    print("\n\n##########Phase 1 : READY DATA##########")
    (doc_id, titles, tokenized_doc, contents) = prs.readyData(ndoc, True)
   
    #파이프라인 불러오기
    ###일단 파이프라인 으로 해보고 안되면 전처리도 따로 코드 만들어서 넣기!!!####
    pipe=joblib.load('/home/dapi2/TIBigdataMiddleware/SVM.h5')

    #모델을 이용하여 예측
    predicted_svm=pipe.predict(tokenized_doc)##column 이름 바꾸기
    print("SVM")
    return predicted_svm
"""
    SVM_PRE = "../../../TIBigdataFE/src/assets/entire_tfidf/svm_data.json"

    if DOWNLOAD_DATA_OPTION == True:
        with open(SVM_PRE, 'w', -1, "utf-8") as f:
            json.dump(predicted_svm, f, ensure_ascii=False)
"""    
    
    