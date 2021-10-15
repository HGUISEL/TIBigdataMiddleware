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
import traceback

logger = logging.getLogger("flask.app.kmeans")
#logging.basicConfig(level=logging.INFO, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
#logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
#logging.basicConfig(filename = "kmeans_debug.log", level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

def kmeans(email, keyword, savedDate, optionList, analysisName):
    identification = str(email)+'_'+analysisName+'_'+str(savedDate)+"// "

    if (str(type(int(optionList))) != "<class 'int'>" ):
        logger.info(identification + "군집수는 양의 정수여야 합니다" + str(type(int(optionList))))
        return "failed", "군집수는 양의 정수이어야 합니다. "
    
    try:
        logger.info(identification + "빈도수분석 정보를 가져옵니다.")
        top_words = getCount(email, keyword, savedDate, optionList)
        if top_words is None:
            logger.info(identification+"빈도수 분석 정보가 없습니다. 빈도수 분석을 먼저 실시합니다. ")
            word_count(email, keyword, savedDate, optionList, "wordcount")
            top_words = getCount(email, keyword, savedDate, optionList)[0]
        else:
            top_words = top_words[0]
        top_words = json.loads(top_words)
    
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"빈도수분석정보를 가져오는 중에 오류가 발생했습니다. \n"+str(err))
        return "failed", "빈도수분석정보를 가져오는 중에 오류가 발생했습니다. 세부사항: " + str(e)
    try:
    # preprocessed = getPreprocessing(email, keyword, savedDate, optionList)[0]
        preprocessed, titleList = getPreprocessingAddTitle(email, keyword, savedDate, optionList)[0:2]
        logger.info(identification+"mongodb에서 전처리 내용을 가져왔습니다.")
        logger.debug(len(preprocessed))
        logger.debug(preprocessed[0][0:10])

    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"전처리 정보를 가져오는데 실패하였습니다. \n"+str(err))
        return "failed", "전처리 정보를 가져오는데 실패하였습니다. 세부사항:" + str(e)

    try:
        logger.info(identification+"벡터화를 실시합니다.")
        vec = CountVectorizer(analyzer = lambda x:x) # list형태를 input받을 수 있도록 함

        x = vec.fit_transform(preprocessed)
        df = pd.DataFrame(x.toarray(), columns=vec.get_feature_names(), index = titleList)
        logger.info("벡터화 완료")  
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"벡터화과정에서 에러가 발생했습니다. \n"+str(err))
        return "failed", "벡터화과정에서 에러가 발생했습니다. 세부사항:" + str(e)

    try:
        logger.info(identification + "군집분석을 실시합니다.")
        kmeans = KMeans(n_clusters=int(optionList)).fit(df)    
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"문서 개수보다 군집 수가 많습니다. \n"+str(err))
        return "failed", "문서 개수보다 군집 수가 많습니다. 군집수를 문서개수보다 적게 해주시기 바랍니다. 세부사항:" + str(e)

    try:
        logger.info(identification + "분할군집분석 실행(군집수 3개)")
        logger.debug(kmeans.labels_)

        pca = PCA(n_components=2)
        principalComponents=pca.fit_transform(df)
        principalDF = pd.DataFrame(data = principalComponents, columns = ['principal_component_1', 'principal_component_2'])
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"분할군집분석 실행중 오류가 발생했습니다. \n"+str(err))
        return "failed", "분할군집분석 실행중 오류가 발생했습니다. 세부사항:" + str(e)

    try:
        logger.info(identification+"결과를 json파일로 만듭니다.")
        indexList = [ item for item in principalDF.index]
        # https://observablehq.com/@d3/scatterplot-with-shapes

        jsonDict = dict()
        textPCAList = list()
        
        for i in range(len(indexList)):
            textNum = indexList[i]
            textDict = dict()
            textDict["category"] = int(kmeans.labels_[textNum])
            textDict["x"] = int(principalDF["principal_component_1"][textNum])
            textDict['y'] = int(principalDF["principal_component_2"][textNum])
            textDict['title'] = titleList[i]
            textPCAList.append(textDict)
        logger.debug(textPCAList)

    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"분할군집분석 결과를 json파일로 만드는 중에 오류가 발생했습니다. \n"+str(err))
        return "failed", "분할군집분석 결과를 json파일로 만드는 중에 오류가 발생했습니다. 세부사항:" + str(e)
        
    

    # cluster=AgglomerativeClustering(n_clusters= clusterNum, linkage='ward')
    # logger.debug(cluster.fit_predict(df))

    # clusterDict = dict()


    try:
        logger.info(identification + "MongoDB에 데이터를 저장합니다.")
        
        client=MongoClient(host='localhost',port=27017)
        db=client.textMining

        doc={
            "userEmail" : email,
            "keyword" : keyword,
            "savedDate": savedDate,
            "analysisDate" : datetime.datetime.now(),
            #"duration" : ,
            "resultPCAList" : textPCAList,
            #"resultCSV":
        }

        db.kmeans.insert_one(doc) 
        logger.info(identification + "MongoDB에 저장되었습니다.")

    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification + "MongoDB에 결과를 저장하는 중에 오류가 발생했습니다. \n"+str(err))
        return "failed", "MongoDB에 결과를 저장하는 중에 오류가 발생했습니다. 세부사항:" + str(e)

    return True, textPCAList


# kmeans('21800520@handong.edu', '북한', "2021-08-10T10:59:29.974Z", 3, 'kmeans')