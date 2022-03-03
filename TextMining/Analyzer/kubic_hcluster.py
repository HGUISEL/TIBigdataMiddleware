import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname('TextMining/Tokenizer'))))

from numpy.core.records import array


from TextMining.Tokenizer.kubic_morph import *
from TextMining.Tokenizer.kubic_data import *
from TextMining.Tokenizer.kubic_mystorage import *
from TextMining.Analyzer.kubic_wordCount import *

import account.MongoAccount as monAcc

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

from sklearn.datasets import load_iris
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage

import logging

logger = logging.getLogger("flask.app.hcluster")
#logging.basicConfig(level=logging.INFO, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
#logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


def plot_dendrogram(model, **kwargs):
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack([model.children_, model.distances_,
                                      counts]).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)
    return linkage_matrix


import json

def create_tree(linked, titleList):
    ## inner func to recurvise-ly walk the linkage matrix
    def recurTree(tree):
        k = tree['name']
        ## no children for this node
        if k not in inter:
            # title 추가.
            tree["title"] = titleList[int(k)]
            return
        for n in inter[k]:
            ## build child nodes
            node = {
                "name": n,
                "parent": k,
                "children": []
            }
            ## add to children
            tree['children'].append(node)
            ## next recursion
            recurTree(node)      
    
    num_rows, _ = linked.shape
    inter = {}
    i = 0
    # loop linked matrix convert to dictionary
    for row in linked:
        i += 1
        inter[float(i + num_rows)] = [row[0],row[1]]

    # start tree data structure
    tree = {
        "name": float(i + num_rows),
        "parent": None,
        "children": []
    }
    # start recursion
    recurTree(tree)
    return tree

def hcluster(email, keyword, savedDate, optionList, analysisName, treeLevel):
    identification = str(email)+'_'+analysisName+'_'+str(savedDate)+"// "
    try:
        preprocessed, title, nTokens = getPreprocessingAddTitle(email, keyword, savedDate, optionList)
        logger.info("mongodb에서 전처리 내용을 가져왔습니다.")
        logger.debug("문서개수: " + str(len(preprocessed)))
        logger.debug("문서제목: " + str(title))

        vec = CountVectorizer(analyzer = lambda x:x) # list형태를 input받을 수 있도록 함

        x = vec.fit_transform(preprocessed)
        df = pd.DataFrame(x.toarray(), columns=vec.get_feature_names())
        #logger.debug(df["가군"])

        # https://observablehq.com/@d3/scatterplot-with-shapes

        cluster=AgglomerativeClustering(None, distance_threshold=0)
        logger.debug(cluster.fit_predict(df))

        # clusterDict = dict()
        
        model = cluster.fit(df)
        logger.debug("모델: " + str(model))
        # plot the top three levels of the dendrogram
        linkage_matrix = plot_dendrogram(model, truncate_mode='level', p=5)

        result = create_tree(linkage_matrix, title)

        logger.debug(result)


        logger.info("MongoDB에 데이터를 저장합니다.")
        
        client = MongoClient(monAcc.host, monAcc.port)
        db=client.textMining
        now = datetime.datetime.now()
        doc={
            "userEmail" : email,
            "keyword" : keyword,
            "savedDate": savedDate,
            "analysisDate" : now,
            #"duration" : ,
            "result" : result,
            #"resultCSV":
        }

        insterted_doc = db.hcluster.insert_one(doc) 
        analysisInfo = { "doc_id" : insterted_doc.inserted_id, "analysis_date": str(doc['analysisDate'])}
        
        logger.info("MongoDB에 저장되었습니다.")
        return True, result, analysisInfo
    except Exception as e:
        import traceback
        err = traceback.format_exc()
        logger.error(identification +str(err))
        return False, err, None



#hcluster('21800520@handong.edu', '북한', "2021-08-10T10:59:29.974Z", 100, 'hcluster', 3)
# result = hcluster('21800520@handong.edu', '통일', "2021-09-07T06:59:01.626Z", 100, 'hcluster', 3)
# print(result[2])