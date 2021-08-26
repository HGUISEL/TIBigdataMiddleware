import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname('TextMining/Tokenizer'))))

from numpy.core.records import array


from TextMining.Tokenizer.kubic_morph import *
from TextMining.Tokenizer.kubic_data import *
from TextMining.Tokenizer.kubic_mystorage import *
from TextMining.Analyzer.kubic_wordCount import *

import numpy as np
import operator

from bson import json_util

from io import StringIO
import gridfs
import csv
from collections import defaultdict

import pandas as pd
from gensim.models import Word2Vec
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
import scipy.cluster.hierarchy as shc

import logging

logger = logging.getLogger("flask.app.kmeans")
#logging.basicConfig(level=logging.INFO, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
#logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
#logging.basicConfig(filename = "kmeans_debug.log", level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

def kmeans(email, keyword, savedDate, optionList, analysisName, clusterNum):

    top_words = json.loads(getCount(email, keyword, savedDate, optionList)[0])
    preprocessed = getPreprocessing(email, keyword, savedDate, optionList)[0]

    logger.info("mongodb에서 전처리 내용을 가져왔습니다.")
    logger.debug(len(preprocessed[1]))

    vec = CountVectorizer(analyzer = lambda x:x) # list형태를 input받을 수 있도록 함

    x = vec.fit_transform(preprocessed)
    df = pd.DataFrame(x.toarray(), columns=vec.get_feature_names())

    logger.info("DTM생성 완료")
    logger.debug(df)    

    kmeans = KMeans(n_clusters=3).fit(df)   
    logger.info("비계층적 군집분석 실행(군집수 3개)")
    logger.debug(kmeans.labels_)

    pca = PCA(n_components=2)
    principalComponents=pca.fit_transform(df)
    principalDF = pd.DataFrame(data = principalComponents, columns = ['principal_component_1', 'principal_component_2'])
    logger.info("PCA로 2차원화")
    logger.debug(principalDF)
    logger.debug(kmeans.labels_)

    indexList = [ item for item in principalDF.index]

    # https://observablehq.com/@d3/scatterplot-with-shapes

    jsonDict = dict()
    textPCAList = list()
    
    for textNum in indexList:
        textDict = dict()
        textDict["category"] = int(kmeans.labels_[textNum])
        textDict["x"] = int(principalDF["principal_component_1"][textNum])
        textDict['y'] = int(principalDF["principal_component_2"][textNum])
        textPCAList.append(textDict)
    
    logger.debug(textPCAList)
    logger.info("Make kmeans plot graph json file")

    cluster=AgglomerativeClustering(n_clusters= clusterNum, linkage='ward')
    logger.debug(cluster.fit_predict(df))

    clusterDict = dict()


    
    logger.info("MongoDB에 데이터를 저장합니다.")
    
    client=MongoClient(host='localhost',port=27017)
    db=client.textMining

    doc={
        "userEmail" : email,
        "keyword" : keyword,
        "savedDate": savedDate,
        "analysisDate" : datetime.datetime.now(),
        #"duration" : ,
        "resultPCAList" : textPCAList,
        "resultclusterJson" : clusterDict
        #"resultCSV":
    }

    db.kmeans.insert_one(doc) 

    logger.info("MongoDB에 저장되었습니다.")

    return textPCAList, clusterDict


#kmeans('21800520@handong.edu', '북한', "2021-08-10T10:59:29.974Z", 100, 'kmeans', 3)