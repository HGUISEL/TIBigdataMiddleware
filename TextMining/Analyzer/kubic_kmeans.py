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

logger = logging.getLogger()
#logging.basicConfig(level=logging.INFO, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


def kmeans(email, keyword, savedDate, optionList, analysisName):

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
    print(principalDF)

kmeans('21800520@handong.edu', '북한', "2021-08-10T10:59:29.974Z", 100, 'kmeans')