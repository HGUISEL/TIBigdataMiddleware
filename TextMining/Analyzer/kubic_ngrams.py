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
import operator

import logging

logger = logging.getLogger("flask.app.ngrams")

# logger = logging.getLogger()
# logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

def ngrams(email, keyword, savedDate, optionList, analysisName, n):
    logger.info("ngram start")

    preprocessed = getPreprocessing(email, keyword, savedDate, optionList)[0]
    
    bglist = []
    for sentence in preprocessed:
        bglist += list(nltk.ngrams(sentence, n))
    bgCountDict = Counter(bglist)

    sortedBgCountDict = dict(sorted(bgCountDict.items(), key=operator.itemgetter(1), reverse=True))

    top_words = dict()
    i = 0
    for key, v in sortedBgCountDict.items():
      if v > 1 and i < int(optionList):
        for word in key:
            if word in top_words.keys():
                top_words[word] += 1
            else:
                top_words[word] = 1
        logger.debug(str(key) + str(v))
        i += 1

    logger.debug(top_words)

    wordToId = {w:i for i, w in enumerate(top_words.keys())}
    idToWord = {i:w for i, w in enumerate(top_words.keys())}

    adjacent_matrix = np.zeros((len(top_words.keys()), len(top_words.keys())), int)

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
        nodeDict["count"] = top_words[wrd]

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

    logger.debug(jsonDict)

    return jsonDict
    

# ngrams('21600280@handong.edu', '북한', "2021-07-08T11:46:03.973Z", 50, 'tfidf', 3)