import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname('TextMining/Tokenizer'))))

from numpy.core.records import array


from TextMining.Tokenizer.kubic_morph import *
from TextMining.Tokenizer.kubic_data import *
from TextMining.Tokenizer.kubic_mystorage import *
from TextMining.Analyzer.kubic_wordCount import *

import numpy as np

from bson import json_util

from io import StringIO
import gridfs
import csv
from collections import defaultdict

from collections import Counter
import nltk
import networkx as nx

import logging

#logger = logging.getLogger("flask.app.ngrams")

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

def ngrams(email, keyword, savedDate, optionList, analysisName, n):
    logger.info("ngram start")

    top_words = json.loads(getCount(email, keyword, savedDate, optionList)[0])
    preprocessed = getPreprocessing(email, keyword, savedDate, optionList)[0]
    
    bglist = []
    for sentence in preprocessed:
        bglist += list(nltk.ngrams(sentence, n))

    bgCountDict = Counter(bglist)

    # ngramToId = {w:i for i, w in enumerate(bgCountDict.keys())}
    # idTongram = {i:w for i, w in enumerate(bgCountDict.keys())}
    
    # adjacent_matrix = np.zeros((int(optionList), int(optionList)), int)

    # for ngram in bgCountDict.keys():
    #     for wi, i in ngramToId.items():
    #         if wi in sentence:
    #             for wj, j in ngramToId.items():
    #                 if i !=j and wj in sentence:
    #                     adjacent_matrix[i][j] +=1

    wordToId = {w:i for i, w in enumerate(top_words.keys())}
    idToWord = {i:w for i, w in enumerate(top_words.keys())}

    adjacent_matrix = np.zeros((int(optionList), int(optionList)), int)

    for ngram in bgCountDict.keys():
        for wi, i in wordToId.items():
            if wi in ngram:
                for wj, j in wordToId.items():
                    if i !=j and wj in ngram:
                        adjacent_matrix[i][j] +=1

    network = nx.from_numpy_matrix(adjacent_matrix)


    jsonDict = dict()
    nodeList = list()
    for n in network.nodes:
        nodeDict = dict()
        wrd = idToWord[n]
        nodeDict["id"] = int(n)
        nodeDict["name"] = wrd

        nodeList.append(nodeDict)
    
    jsonDict["nodes"] = nodeList

    edgeList = list()
    for s,t in network.edges:
        edgeDict = dict()
        edgeDict["source"] = int(s)
        edgeDict["target"] = int(t)
        edgeDict["weight"] = int(adjacent_matrix[s][t])
        edgeList.append(edgeDict)
    
    jsonDict["links"] = edgeList

    logger.debug(jsonDict["nodes"])


#ngrams('21600280@handong.edu', '북한', "2021-07-08T11:46:03.973Z", 100, 'tfidf', 2)