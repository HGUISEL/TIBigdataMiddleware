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

import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
#logging.basicConfig(level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


def kmeans(email, keyword, savedDate, optionList, analysisName):
    logger.info("mongodb에서 전처리 내용을 가져왔습니다.")
    top_words = json.loads(getCount(email, keyword, savedDate, optionList)[0])
    preprocessed = getPreprocessing(email, keyword, savedDate, optionList)[0]
    logger.debug(preprocessed[1][0:3])

kmeans('21600280@handong.edu', '북한', "2021-07-08T11:46:03.973Z", 100, 'tfidf')