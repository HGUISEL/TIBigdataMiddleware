import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname('TextMining/Tokenizer'))))

from numpy.core.records import array


from TextMining.Tokenizer.kubic_morph import *
from TextMining.Tokenizer.kubic_data import *
from TextMining.Tokenizer.kubic_mystorage import *
from TextMining.Analyzer.kubic_wordCount import *

import numpy as np
import networkx as nx # 새로 추가된 묘듈이다. pip로 추가
import operator

from bson import json_util

from io import StringIO
import gridfs
import csv
from collections import defaultdict


def semanticNetworkAnalysis(email, keyword, savedDate, optionList, analysisName):

    '''
    graph json 만들기
    '''
    print("mongodb에서 전처리 내용을 가져왔습니다.")
    top_words = json.loads(getCount(email, keyword, savedDate, optionList)[0])
    preprocessed = getPreprocessing(email, keyword, savedDate, optionList)[0]
    

    wordToId = {w:i for i, w in enumerate(top_words.keys())}
    idToWord = {i:w for i, w in enumerate(top_words.keys())}

    adjacent_matrix = np.zeros((int(optionList), int(optionList)), int)

    for sentence in preprocessed:
        for wi, i in wordToId.items():
            if wi in sentence:
                for wj, j in wordToId.items():
                    if i !=j and wj in sentence:
                        adjacent_matrix[i][j] +=1
    network = nx.from_numpy_matrix(adjacent_matrix)


    def id2word(d):
        new_d = {}
        for i,w in d.items():
            new_d[idToWord[i]] = w
        return new_d


    # 각 단어:중심성 dict만들기
    degree_cen = id2word(nx.degree_centrality(network))
    eigenvector_cen = id2word(nx.eigenvector_centrality(network))
    closeness_cen = id2word(nx.closeness_centrality(network))
    between_cen = id2word(nx.current_flow_betweenness_centrality(network))




    # 네트워크용 json 만들기

    jsonDict = dict()
    nodeList = list()
    for n in network.nodes:
        nodeDict = dict()
        wrd = idToWord[n]
        nodeDict["id"] = int(n)
        nodeDict["name"] = wrd
        nodeDict["degree_cen"] = degree_cen[wrd]
        nodeDict["eigenvector_cen"] = eigenvector_cen[wrd]
        nodeDict["closeness_cen"] = closeness_cen[wrd]
        nodeDict["between_cen"] = between_cen[wrd]

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




    # 큰 순서대로 sort
    sorted_degree_cen = dict(sorted(degree_cen.items(), key=lambda item: item[1], reverse = True))
    sorted_eigenvector_cen = dict(sorted(eigenvector_cen.items(), key=lambda item: item[1], reverse = True))
    sorted_closeness_cen = dict(sorted(closeness_cen.items(), key=lambda item: item[1], reverse = True))
    sorted_between_cen = dict(sorted(between_cen.items(), key=lambda item: item[1], reverse = True))

    # dataframe 만들기
    cen_dict = { "count": top_words, "degree_cen": sorted_between_cen , "eigenvector_cen": sorted_eigenvector_cen, "closeness_cen": sorted_closeness_cen, "between_cen": sorted_between_cen}


    print("MongoDB에 데이터를 저장합니다.")



    client=MongoClient(host='localhost',port=27017)
    db=client.textMining

    doc={
        "userEmail" : email,
        "keyword" : keyword,
        "savedDate": savedDate,
        "analysisDate" : datetime.datetime.now(),
        #"duration" : ,
        "resultGraphJson" : jsonDict,
        "resultCenJson" : cen_dict
        #"resultCSV":
    }

    #db.network.insert_one(doc) 
    print("MongoDB에 저장되었습니다.")


    return jsonDict, cen_dict
    







semanticNetworkAnalysis('21600280@handong.edu', '북한', "2021-07-08T11:46:03.973Z", 100, 'tfidf')
#semanticNetworkAnalysis('21600280@handong.edu', '북한', "2021-07-08T11:46:03.973Z", 100, 'tfidf')
