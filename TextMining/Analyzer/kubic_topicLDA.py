import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname('TextMining/Tokenizer'))))

import numpy as np
import pandas as pd
import gensim  # LDA를 위한 라이브러리

from TextMining.Tokenizer.kubic_morph import *
from TextMining.Tokenizer.kubic_data import *
from TextMining.Tokenizer.kubic_mystorage import *

import account.MongoAccount as monAcc

import logging
import traceback

logger = logging.getLogger("flask.app.topicLDA")

def to_docList(corpus):
    docList = []
    for doc in corpus:
        sentenceList = []
        for sentence in doc:
            sentenceList += sentence
        docList.append(sentenceList)
    return docList

def topicLDA(email, keyword, savedDate, optionList, analysisName):
    identification = str(email)+'_'+analysisName+'_'+str(savedDate)+"// "

    try:
        int(optionList)
        if not(0 <= int(optionList)):
            raise Exception("군집의 수는 양의 정수여야 합니다 입력된 값:" + str(optionList))
    except Exception as e:
        err = traceback.format_exc()
        logger.info(identification + "군집의 수는 양의 정수여야 합니다 입력된 값:" + str(err))
        #print(identification + "분석할 단어수는 양의 정수여야 합니다" + str(err))
        return "failed", "군집의 수는 양의 정수이어야 합니다.", None

    try:
        logger.info(identification + "전처리 정보를 가져옵니다.")
        preprocessed = getPreprocessing(email, keyword, savedDate, optionList)[0]
        preprocessed = to_docList(preprocessed)
        #logger.error(preprocessed)
        # print(len(preprocessed))
        # for i in range(len(preprocessed)):
        #     print(i,"번째 문서의 길이:",len(preprocessed[i]))
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"전처리 정보를 가져오는데 실패하였습니다. \n"+str(err))
        return "failed", "전처리 정보를 가져오는데 실패하였습니다. 세부사항:" + str(e), None

    # try:
    #     logger.info(identification + "LDA분석을 실시합니다.")
    #     logger.info(identification + "LDA모델을 만듭니다.")

    #     LDA_bigram = gensim.models.Phrases(preprocessed)
    #     LDA_trigram = gensim.models.Phrases(LDA_bigram[preprocessed])

    #     LDA_bigram_model = gensim.models.phrases.Phraser(LDA_bigram)
    #     LDA_trigram_model = gensim.models.phrases.PHraser(LDA_trigram)

    # except Exception as e:
    #     err = traceback.format_exc()
    #     logger.error(identification+"LDA모델을 만드는데 실패하였습니다. \n"+str(err))
    #     return "failed", "LDA모델을 만드는데 실패하였습니다. 세부사항:" + str(e)
    
    try: # 각 단어를 (word_id, word_frequency)의 형태로 바꾸기
        logger.info(identification + "LDA분석을 실시합니다.")
        logger.info(identification + "각 단어를 (word_id, word_frequency)의 형태로 바꿉니다.")

        from gensim import corpora
        dictionary = corpora.Dictionary(preprocessed)
        corpus = [dictionary.doc2bow(text) for text in preprocessed]
        # print(corpus[0]) # 수행된 결과에서 첫번째 문서 출력.
        # print(dictionary[1949]) # 위의 결과에서 id가 1949인 단어 확인.

    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"각 단어를 (word_id, word_frequency)의 형태로 바꾸는것에 실패하였습니다. \n"+str(err))
        return "failed", "각 단어를 (word_id, word_frequency)의 형태로 바꾸는것에 실패하였습니다. 세부사항:" + str(e), None       
    
    try: # LDA모델 훈련
        logger.info(identification + "LDA모델 학습을 시작합니다.")
        NUM_TOPICS = int(optionList)
        NUM_PASSES = 20 # 학습 수는...

        # 추후에
        # early stop option 적용 해야함.
        # gensim.models.ldamodel 멀티코어..?
        # gensim.models.lda_worker --> 병렬처리 할 수 있는 코드로 구현해보기.
        ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics = NUM_TOPICS, id2word=dictionary, passes=NUM_PASSES)
        topics = ldamodel.print_topics(num_words = 4)#각 토픽의 단어 4개씩 프린트

        # for topic in topics:
        #     print(topic)

    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"LDA모델 학습실패 \n"+str(err))
        return "failed", "LDA모델 학습실패 세부사항:" + str(e), None

    try: # LDA시각화

        # 문서 별 토픽의 비율 확인
        # for i, topic_list in enumerate(ldamodel[corpus]):
        #     print(i,'번째 문서의 topic 비율은',topic_list)

        # 토픽별 단어의 비율 및 토픽의 분포(거리, 크기) 확인
        import pyLDAvis
        import pyLDAvis.gensim as gensimvis
        from IPython.core.display import display, HTML

        prepared_data = gensimvis.prepare(ldamodel, corpus, dictionary)
        # pyLDAvis.save_html(prepared_data, 'LDA_Visualization.html')
        # pyLDAvis.save_json(prepared_data, 'LDA_Visualization.json') #to_dict

        # https://github.com/bmabey/pyLDAvis/blob/8e534a6e1852ef4674ef9a45223e8c6a931db2e6/pyLDAvis/_display.py#L114
        result_dict = prepared_data.to_dict()
        

    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"LDA모델 시각화 실패 \n"+str(err))
        return "failed", "LDA모델 시각화 실패 세부사항:" + str(e), None
    try:
        client = MongoClient(monAcc.host, monAcc.port)
        #print('MongoDB에 연결을 성공했습니다.')
        logger.info(identification+ "MongoDB연결 성공")
        db=client.textMining
        nTokens = optionList
        now = datetime.datetime.now()
        doc={
            "userEmail" : email,
            "keyword" : keyword,
            "savedDate": savedDate,
            "analysisDate" : now,
            #"duration" : ,
            "nTokens" : nTokens,
            "result_graph" : json.dumps(result_dict, ensure_ascii=False),
            # "resultBar" : barBinary,
            # "resultWC" : wcBinary,
            #"resultCSV" :,
        }
        insterted_doc = db.topicLDA.insert_one(doc)  
        analysisInfo = { "doc_id" : insterted_doc.inserted_id, "analysis_date": str(doc['analysisDate'])}

        logger.info(identification+ "MongoDB에 결과 저장")

    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"분석결과 MongoDB저장 중 에러발생. \n"+str(err))
        return "failed", "결과를 저장하는 과정에서 오류가 발생했습니다. \n 세부사항:" + str(e), None

    return True, result_dict, analysisInfo

# result = topicLDA('21800520@handong.edu', '북한', "2021-09-07T07:01:07.137Z", "4", 'LDA')
# print(result[2])