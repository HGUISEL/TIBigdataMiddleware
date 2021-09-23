import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname('TextMining/Tokenizer'))))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from wordcloud import WordCloud
from sklearn.feature_extraction.text import CountVectorizer

from TextMining.Tokenizer.kubic_morph import *
from TextMining.Tokenizer.kubic_data import *
from TextMining.Tokenizer.kubic_mystorage import *

from io import StringIO
import gridfs
import csv

import logging
import traceback

logger = logging.getLogger("flask.app.wordCount")

## CountVectorizer 빈도수 계산
def word_count(email, keyword, savedDate, optionList, analysisName):    
    # mongo에서 전처리 결과 가져오기
    identification = str(email)+'_'+analysisName+'_'+str(savedDate)+"// "

    logger.info(identification+ "전처리 내용을 가져옵니다.")

    doc, nTokens = getPreprocessing(email, keyword, savedDate, optionList)
    if doc == "failed":
        return doc, nTokens
    else:
        doc = sum(doc, []) # 중첩리스트 하나로 합치기
        logger.info(identification+ "전처리 내용을 성공적으로 가져왔습니다.")
        #print(doc, nTokens)    
    
    try:
        logger.info(identification+ "전처리 내용을 벡터화 합니다.")
        vectorizer = CountVectorizer(analyzer='word', max_features=int(optionList), tokenizer=None)
        words=vectorizer.fit(doc)
        words_fit = vectorizer.fit_transform(doc)
    
        word_list=vectorizer.get_feature_names() #=sorted(vectorizer.vocabulary_)
        #print("Vec사전:", word_list, '\n빈도수:', words_fit.toarray().sum(axis=0))
        count_list = words_fit.toarray().sum(axis=0)

    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"백터화 과정에서 에러가 발생했습니다. \n"+str(err))
        return "failed", "백터화 과정에서 에러가 발생했습니다. \n 세부사항:" + str(e)

    try:
        logger.info(identification+ "벡터화 이후 빈도수 분석을 진행합니다.")
        df=pd.DataFrame()
        df["words"] = word_list
        df["count"] = count_list

        count_list = list([int(x) for x in count_list])
        df = df.sort_values(by=['count'], axis=0, ascending=False)
        #dict_words = dict(zip(word_list,count_list))
        dict_words = df.set_index('words').T.to_dict('records') #type: list
        dict_words = dict_words[0]

        list_graph = list()

        for key, value in dict_words.items():
            node_dict = dict()
            node_dict["word"] = key
            node_dict["value"] = int(value)
            list_graph.append(node_dict)
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"빈도수 분석 과정에서 에러가 발생했습니다. \n"+str(err))
        return "failed", "빈도수 분석 과정에서 에러가 발생했습니다. \n 세부사항:" + str(e)

    # print("빈도수 분석결과\n", df, '\n', dict_words)
    # print(list_graph)

    ## CSV파일로 저장
    # with open('wc_csvfile.csv','w') as f:
    #     w = csv.writer(f)
    #     for k, v in dict_words.items():
    #         w.writerow([k, v])

    # ## Barchart 그리기
    # FONT_PATH='TextMining/NanumBarunGothic.ttf'
    # fontprop = fm.FontProperties(fname=FONT_PATH, size=8)
    # plt.figure(figsize=(20,5))
    # plt.bar(word_list, count_list)
    # plt.xticks(rotation=40, ha='right', fontproperties=fontprop)
    # plt.savefig('wc_barchart.jpg')

    # ## Wordcloud 시각화
    # wordcloud = WordCloud(
    #     font_path = FONT_PATH,
    #     width = 1500,
    #     height = 1000,
    #     background_color="white",
    # )
    # wordcloud = wordcloud.generate_from_frequencies(dict_words)
    # #plt.savefig('wordcould.png', bbox_inches='tight')
    # print("빈도수분석 Wordcloud 결과파일이 생성되었습니다..")
    # wordcloud.to_file('wc_wordcloud.jpg')
    
    
    # #Mongo에 저장된 바차트, 워드클라우드의 binary 파일과 이미지파일이 일치하는지 확인하기 위해 size출력
    # from os.path import getsize
    # BarFile = 'wc_barchart.jpg'    
    # WcFile = 'wc_wordcloud.jpg'
    # bar_file_size = getsize(BarFile) #wc_barchart.jpg: 95129
    # wc_file_size = getsize(WcFile) #wc_wordcloud.jpg: 223997

    # print('File Name: %s \tFile Size: %d' %(BarFile, bar_file_size))
    # print('File Name: %s \tFile Size: %d' %(WcFile, wc_file_size))
    
    ### Mongo 저장 ###
    client=MongoClient(host='localhost',port=27017)
    #print('MongoDB에 연결을 성공했습니다.')
    logger.info(identification+ "MongoDB연결 성공")
    db=client.textMining
    nTokens = optionList
    now = datetime.datetime.now()
    #print("time: ", now,'\n', now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")) #형식
    
    # ## 몽고에 Barchart 이미지 binary로 저장
    # print("\nMongoDB에 빈도수 분석 결과를 바차트로 저장합니다.")
    # fs = gridfs.GridFS(db, 'count') #count.files, count.chunks로 생성됨
    # with open(BarFile, 'rb') as f:
    #     contents = f.read()
    # fs.put(contents, filename='wc_bar')

    # ## 몽고의 count.files & count.chunks collection에 WordCloud 이미지 binary로 저장
    # print("MongoDB에 빈도수 분석 결과를 wordcloud로 저장합니다.\n")
    # with open(WcFile, 'rb') as f:
    #     contents = f.read()
    # fs.put(contents, filename='wc_wordcloud')

    # barBinary = getBinaryImage(bar_file_size, analysisName)
    # wcBinary = getBinaryImage(wc_file_size, analysisName)

    doc={
        "userEmail" : email,
        "keyword" : keyword,
        "savedDate": savedDate,
        "analysisDate" : datetime.datetime.now(),
        #"duration" : ,
        "nTokens" : nTokens,
        "result_graph" : json.dumps(list_graph, ensure_ascii=False),
        "result_table" : json.dumps(dict_words, ensure_ascii=False),
        # "resultBar" : barBinary,
        # "resultWC" : wcBinary,
        #"resultCSV" :,
    }
    db.count.insert_one(doc)  
    
    logger.info(identification+ "MongoDB에 결과 저장")
    
    return dict_words, list_graph
 
#word_count('21600280@handong.edu', '북한', "2021-07-08T11:46:03.973Z", 100, 'count')