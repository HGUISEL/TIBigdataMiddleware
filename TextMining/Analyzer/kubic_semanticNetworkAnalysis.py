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

def cal_percentile(edges, matrix, linkStrength):
    weightList = list()
    for s,t in edges:
        weightList.append(int(matrix[s][t]))
    weightArr = np.array(weightList)
    percentile = np.percentile(weightArr, linkStrength)
    return percentile

def filter_links(edges, matrix, linkStrength, minWeight, maxWeight):
    print("최소, 최대값:",minWeight, maxWeight)
    if linkStrength == 100 or minWeight == maxWeight:
        edgeList = list()
        for s,t in edges:
            edgeDict = dict()
            edgeDict["source"] = int(s)
            edgeDict["target"] = int(t) 
            edgeDict["weight"] = int(matrix[s][t])
            edgeList.append(edgeDict)
        logger.debug(str(len(edgeList)))
        return edgeList
    elif linkStrength == 0:
        return None
    else:
        # 최대값에서 최소값을 뺴서 값으 범위값을 구하고, 그 범위에서 사용자가 원하는 퍼센트만큼의 임계치를 구한다.
        strengthVal = ( maxWeight - minWeight ) * (int(linkStrength) / 100) 
        edgeList = list()
        linkedEdgeIDList = list()
        percentile = cal_percentile(edges, matrix,linkStrength)
        # 임계치보다 높은 weight값의 link만 append한다.
        for s,t in edges:
            edgeDict = dict()
            edgeDict["source"] = int(s)
            edgeDict["target"] = int(t) 
            if int(matrix[s][t]) > percentile:
                # print("카운트", int(matrix[s][t]))
                edgeDict["weight"] = int(matrix[s][t])
                edgeList.append(edgeDict)
                linkedEdgeIDList.append(int(s))
                linkedEdgeIDList.append(int(t))
            # else:
            #     print("노카운트", int(matrix[s][t]))
        
        linkedEdgeIDList = list(set(linkedEdgeIDList))

        print(minWeight, maxWeight, percentile, strengthVal+minWeight)
        return edgeList, linkedEdgeIDList
    
        

def semanticNetworkAnalysis(email, keyword, savedDate, optionList, analysisName, linkStrength):
    '''
    graph json 만들기
    '''
    identification = str(email)+'_'+analysisName+'_'+str(savedDate)+"// "
    
    try:
        int(optionList)
        if not(0 <= int(optionList)):
            raise Exception("분석할 단어수는 양의 정수여야 합니다. 입력된 값: "+ str(optionList))
    except Exception as e:
        err = traceback.format_exc()
        logger.info(identification + "분석할 단어수는 양의 정수여야 합니다" +str(err))
        #print(identification + "분석할 단어수는 양의 정수여야 합니다" +str(err))
        return "failed", "분석할 단어수는 양의 정수이어야 합니다. ", None
    
    try:
        int(linkStrength)
        if not(0 <= int(linkStrength) <= 100):
            raise Exception("연결강도는 0~100 사이의 양의 정수여야 합니다")
    except Exception as e:
        err = traceback.format_exc()
        #print(identification + "연결강도는 0~100 사이의 양의 정수여야 합니다" +str(err))
        logger.info(identification + "연결강도는 0~100 사이의 양의 정수여야 합니다" +str(err))
        return "failed", "연결강도는 0~100 사이의 양의 정수여야 합니다 ", None


    try:
        # logger.info(identification + "빈도수분석 정보를 가져옵니다.")
        # top_words = getCount(email, keyword, savedDate, optionList)
        # if top_words is None:
        #     logger.info(identification+"빈도수 분석 정보가 없습니다. 빈도수 분석을 먼저 실시합니다. ")
        #     word_count(email, keyword, savedDate, optionList, "wordcount")
        #     top_words = getCount(email, keyword, savedDate, optionList)[0]
        # else:
        #     top_words = top_words[0]
        # top_words = json.loads(top_words)

        logger.info(identification + "빈도수분석을 실시합니다.")
        top_words = word_count(email, keyword, savedDate, optionList, "wordcount", save = False)[0]

        # print(optionList)
        # print(top_words)
        # print(len(top_words))

    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"의미연결망 분석을 위해 빈도수분석을 실행하는 도중에 오류가 발생했습니다. \n"+str(err))
        return "failed", "의미연결망 분석을 위해 빈도수분석을 실행하는 중에 오류가 발생했습니다. 세부사항: " + str(e), None
    
    try:
        logger.info(identification + "전처리 정보를 가져옵니다.")
        preprocessed = getPreprocessing(email, keyword, savedDate, optionList)[0]
        #logger.error(preprocessed)
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"전처리 정보를 가져오는데 실패하였습니다. \n"+str(err))
        return "failed", "전처리 정보를 가져오는데 실패하였습니다. 세부사항:" + str(e), None
    

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
        return "failed", "연결망 생성을 위한 사전 생성에 실패하였습니다. 세부사항:" + str(e), None

    try:
        logger.info(identification + "연결망 생성")
        adjacent_matrix = np.zeros((int(optionList), int(optionList)), int)

        for doc in preprocessed:
            for sentence in doc:
                for wi, i in wordToId.items():
                    if wi in sentence:
                        for wj, j in wordToId.items():
                            if i !=j and wj in sentence:
                                adjacent_matrix[i][j] +=1
        network = nx.from_numpy_matrix(adjacent_matrix)
        
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"연결망 생성에 실패하였습니다. \n"+str(err))
        return "failed", "연결망 생성에 실패하였습니다. 세부사항:" + str(e), None

    try:
        def id2word(d):
            new_d = {}
            for i,w in d.items():
                try:# 개수만큼 자르기!
                    new_d[idToWord[i]] = w
                except:
                   pass
            return new_d
        
        logger.info(identification+"연결망 분석 결과를 json형태로 변환")
        # 각 단어:중심성 dict만들기
        logger.info(identification+"각 단어: 중심성 dict만들기")
        
        if nx.is_connected(network):
            degree_cen = id2word(nx.degree_centrality(network))
            eigenvector_cen = id2word(nx.eigenvector_centrality(network))
            closeness_cen = id2word(nx.closeness_centrality(network))
            between_cen = id2word(nx.current_flow_betweenness_centrality(network))

    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"단어별 중심성 사전 만들기에 실패했습니다. \n"+str(err))
        return "failed", "단어별 중심성 사전 만들기에 실패했습니다. 세부사항:" + str(e), None


    try:
        # 네트워크용 json 만들기
        logger.info(identification+"네트워크 그래프용 json 만들기")
        jsonDict = dict()
        nodeList = list()
        linkedEdgeIDList = list()
        # print(nodeList)
        jsonDict["links"],linkedEdgeIDList  = filter_links(network.edges, adjacent_matrix, int(linkStrength), np.min(adjacent_matrix[adjacent_matrix>0]), np.max(adjacent_matrix))
        
        print(idToWord)
        print(network.nodes)
        if nx.is_connected(network):
            for n in network.nodes:
                # if int(n) in linkedEdgeIDList:
                nodeDict = dict()
                wrd = idToWord[n]
                nodeDict["id"] = int(n)
                nodeDict["name"] = wrd
                nodeDict["degree_cen"] = degree_cen[wrd]
                nodeDict["eigenvector_cen"] = eigenvector_cen[wrd]
                nodeDict["closeness_cen"] = closeness_cen[wrd]
                nodeDict["between_cen"] = between_cen[wrd]
                nodeDict["count"] = top_words[wrd]

                nodeList.append(nodeDict)
        # else:
        #     for n in network.nodes:
        #         nodeDict = dict()
        #         wrd = idToWord[n]
        #         nodeDict["id"] = int(n)
        #         nodeDict["name"] = wrd

        #         nodeList.append(nodeDict)
        
        jsonDict["nodes"] = nodeList
        # 큰 순서대로 sort
        if nx.is_connected(network):
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
        if nx.is_connected(network):
            cen_dict = { "count": table_to_graph(top_words), 
                        "degree_cen": table_to_graph(sorted_between_cen) , 
                        "eigenvector_cen": table_to_graph(sorted_eigenvector_cen), 
                        "closeness_cen": table_to_graph(sorted_closeness_cen), 
                        "between_cen": table_to_graph(sorted_between_cen)}
        else:
            cen_dict = {"count": table_to_graph(top_words)}
        # print("MongoDB에 데이터를 저장합니다.")
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"결과를 json형식으로 만드는데 실패하였습니다. \n"+str(err))
        return "failed", "결과를 json형식으로 만드는데 실패하였습니다. 세부사항:" + str(e), None

    try:
        logger.info(identification + "MongoDB에 데이터를 저장합니다.")
        client = MongoClient(monAcc.host, monAcc.port)
        db=client.textMining
        now = datetime.datetime.now()

        doc={
            "userEmail" : email,
            "keyword" : keyword,
            "savedDate": savedDate,
            "analysisDate" : now,
            #"duration" : ,
            "resultGraphJson" : jsonDict,
            "resultCenJson" : cen_dict
            #"resultCSV":
        }

        insterted_doc = db.network.insert_one(doc) 
        analysisInfo = { "doc_id" : insterted_doc.inserted_id, "analysis_date": str(doc['analysisDate'])}
        logger.info(identification + "MongoDB에 저장되었습니다.")
        
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification + "MongoDB에 결과를 저장하는 중에 오류가 발생했습니다. \n"+str(err))
        return "failed", "MongoDB에 결과를 저장하는 중에 오류가 발생했습니다. 세부사항:" + str(e)

    return jsonDict, cen_dict, analysisInfo
    






# # 3 차원
result = semanticNetworkAnalysis('21800520@handong.ac.kr', '사드', '2022-04-24T06:51:40.934Z', "10", 'network', "50")
print(result[0])