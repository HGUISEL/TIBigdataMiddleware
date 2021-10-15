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

import logging
import traceback

logger = logging.getLogger("flask.app.network")


def filter_links(edges, matrix, linkStrength, minWeight, maxWeight):
    if linkStrength == 100 or minWeight == maxWeight:
        return edgeList
    elif linkStrength == 0:
        return None
    else:
        strengthVal = ( maxWeight - minWeight ) * (int(linkStrength) / 100) 
        edgeList = list()
        for s,t in edges:
            edgeDict = dict()
            edgeDict["source"] = int(s)
            edgeDict["target"] = int(t) 
            if int(matrix[s][t]) > strengthVal + minWeight:
                edgeDict["weight"] = int(matrix[s][t])
                edgeList.append(edgeDict)

        print(minWeight, maxWeight, strengthVal)
        return edgeList
    
        

def semanticNetworkAnalysis(email, keyword, savedDate, optionList, analysisName, linkStrength):

    '''
    graph json 만들기
    '''
    identification = str(email)+'_'+analysisName+'_'+str(savedDate)+"// "
    
    if (str(type(int(optionList))) != "<class 'int'>" ):
        logger.info(identification + "분석할 단어수는 양의 정수여야 합니다" + str(type(int(optionList))))
        return "failed", "분석할 단어수는 양의 정수이어야 합니다. "
    
    if str(type(int(linkStrength))) != "<class 'int'>" or not ( 0 <= int(linkStrength) <= 100):
        logger.info(identification + "연결강도는 0~100 사이의 양의 정수여야 합니다" + str(type(int(optionList))))
        return "failed", "연결강도는 0~100 사이의 양의 정수여야 합니다 "


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
        logger.info(identification + "전처리 정보를 가져옵니다.")
        preprocessed = getPreprocessing(email, keyword, savedDate, optionList)[0]
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"전처리 정보를 가져오는데 실패하였습니다. \n"+str(err))
        return "failed", "전처리 정보를 가져오는데 실패하였습니다. 세부사항:" + str(e)
    

    try:
        logger.info(identification + "연결망 생성을 위한 사전생성")
        wordToId = dict()
        for w, i in enumerate(top_words.keys()):
            wordToId[i] = w
            if w == int(optionList)-1:
                break
        
        idToWord = dict()
        for i, w in enumerate(top_words.keys()):
            idToWord[i] = w
            if i == int(optionList)-1:
                break
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"연결망 생성을 위한 사전 생성에 실패하였습니다. \n"+str(err))
        return "failed", "연결망 생성을 위한 사전 생성에 실패하였습니다. 세부사항:" + str(e)

    try:
        logger.info(identification + "연결망 생성")
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

    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"연결망 생성에 실패하였습니다. \n"+str(err))
        return "failed", "연결망 생성에 실패하였습니다. 세부사항:" + str(e)

    try:
        logger.info(identification+"연결망 분석 결과를 json형태로 변환")
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
        # print(nodeList)

        jsonDict["links"] = filter_links(network.edges, adjacent_matrix, linkStrength, np.min(adjacent_matrix[adjacent_matrix>0]), np.max(adjacent_matrix))

        # 큰 순서대로 sort
        sorted_degree_cen = dict(sorted(degree_cen.items(), key=lambda item: item[1], reverse = True))
        sorted_eigenvector_cen = dict(sorted(eigenvector_cen.items(), key=lambda item: item[1], reverse = True))
        sorted_closeness_cen = dict(sorted(closeness_cen.items(), key=lambda item: item[1], reverse = True))
        sorted_between_cen = dict(sorted(between_cen.items(), key=lambda item: item[1], reverse = True))


        def table_to_graph(t_dict):
            g_list = list()
            for key, value in t_dict.items():
                g_dict = dict()
                g_dict['word'] = key
                g_dict['value'] = value
                g_list.append(g_dict)
            return g_list

        # dataframe 만들기
        cen_dict = { "count": table_to_graph(top_words), 
                    "degree_cen": table_to_graph(sorted_between_cen) , 
                    "eigenvector_cen": table_to_graph(sorted_eigenvector_cen), 
                    "closeness_cen": table_to_graph(sorted_closeness_cen), 
                    "between_cen": table_to_graph(sorted_between_cen)}
        # print("MongoDB에 데이터를 저장합니다.")
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"결과를 json형식으로 만드는데 실패하였습니다. \n"+str(err))
        return "failed", "결과를 json형식으로 만드는데 실패하였습니다. 세부사항:" + str(e)

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
            "resultGraphJson" : jsonDict,
            "resultCenJson" : cen_dict
            #"resultCSV":
        }

        db.network.insert_one(doc) 
        logger.info(identification + "MongoDB에 저장되었습니다.")
        
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification + "MongoDB에 결과를 저장하는 중에 오류가 발생했습니다. \n"+str(err))
        return "failed", "MongoDB에 결과를 저장하는 중에 오류가 발생했습니다. 세부사항:" + str(e)

    return jsonDict, cen_dict
    







#semanticNetworkAnalysis('21600280@handong.edu', '북한', "2021-07-08T11:46:03.973Z", 100, 'tfidf')
#semanticNetworkAnalysis('21800520@handong.edu', '북한', "2021-08-10T10:59:29.974Z", 100, 'network', 50)
