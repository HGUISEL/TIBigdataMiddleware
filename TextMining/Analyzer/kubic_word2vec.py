import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname('TextMining/Tokenizer'))))

import numpy as np
import pandas as pd
import gensim  # LDA를 위한 라이브러리

from TextMining.Tokenizer.kubic_morph import *
from TextMining.Tokenizer.kubic_data import *
from TextMining.Tokenizer.kubic_mystorage import *
from TextMining.Analyzer.kubic_wordCount import *

from gensim.models import Word2Vec
from sklearn.manifold import TSNE
from matplotlib import font_manager as fm
from matplotlib import rc

import logging
import traceback

logger = logging.getLogger("flask.app.word2vec")

# 리스트 받아서 0~1값으로 min-maz normalize
def normalization(x):
    min_value = min(x)
    max_value = max(x) 

    return list(map(lambda x: (x-min_value)/(max_value-min_value), x))

def make_normalization_model(un_norm_list):
    norm_list = normalization(un_norm_list)
    model_dict = dict()
    for i in range(len(un_norm_list)):
        model_dict[un_norm_list[i]] = norm_list[i]
    return model_dict



def cut_with_option(list,email, keyword, savedDate, optionList):
    top_words = word_count(email, keyword, savedDate, optionList, "wordcount")[0]
    result_lst = []
    for word in top_words.keys():
        if word in list:
            result_lst.append(word)
        else:
            logger.info(identification + "단어가 모델에 존재하지 않습니다. 단어:" + word)
    #print(top_words)

    return result_lst, top_words

def word2vec(email, keyword, savedDate, optionList, analysisName):
    identification = str(email)+'_'+analysisName+'_'+str(savedDate)+"// "

    try: # 오류메세지 수정해야함
        int(optionList)
        if not(0 <= int(optionList)):
            raise Exception("군집의 수는 양의 정수여야 합니다 입력된 값:" + str(optionList))
    except Exception as e:
        err = traceback.format_exc()
        logger.info(identification + "군집의 수는 양의 정수여야 합니다 입력된 값:" + str(err))
        #print(identification + "분석할 단어수는 양의 정수여야 합니다" + str(err))
        return "failed", "군집의 수는 양의 정수이어야 합니다."

    try:
        logger.info(identification + "전처리 정보를 가져옵니다.")
        preprocessed = getPreprocessing(email, keyword, savedDate, optionList)[0]
        #logger.error(preprocessed)
        print("문서의 개수:",len(preprocessed))
        for i in range(len(preprocessed)):
            print(i,"번째 문서의 단어 수:",len(preprocessed[i]))
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"전처리 정보를 가져오는데 실패하였습니다. \n"+str(err))
        return "failed", "전처리 정보를 가져오는데 실패하였습니다. 세부사항:" + str(e)

    
    try: # word2vec 모델 만들기
        logger.info(identification + "word2vec 분석을 실시합니다.")
        logger.info(identification + "word2vec 모델 만들기")

        w2v = Word2Vec(preprocessed, min_count =1)
        #print(w2v)
        # print(w2v.wv.most_similar("최고"))

    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"word2vec 모델 만들기에 실패하였습니다. \n"+str(err))
        return "failed", "word2vec 모델 만들기에 실패하였습니다. 세부사항:" + str(e)        
    
    try: # word2vec 시각화를 위한 차원축소
        logger.info(identification + "LDA모델 학습을 시작합니다.")
        
        w2v_tsne = TSNE(n_components=2)
        #w2v_vocab = list(w2v.wv.key_to_index)
        w2v_vocab, top_words = cut_with_option(list(w2v.wv.key_to_index), email, keyword, savedDate, optionList)
        # w2v_vocab = list(w2v.wv.key_to_index.keys())
        #print(w2v_vocab[0:10]) 
        w2v_similarity = w2v.wv[w2v_vocab] # 기존: w2v[word] --> 바뀐 코드: w2v.wv[word]
        transorm_similarity = w2v_tsne.fit_transform(w2v_similarity)
        w2v_df = pd.DataFrame(transorm_similarity, index = w2v_vocab, columns=["x", "y"])

        # print(w2v_df[0:10])

        w2v_df = w2v_df[0:int(optionList)]

        indexList = [ item for item in w2v_df.index]
        # https://observablehq.com/@d3/scatterplot-with-shapes

        jsonDict = dict()
        textTSNEList = list()
        
        # 시각화를 위한 빈도수 정규화 모델
        norm_dict = make_normalization_model(list(top_words.values()))
        for i in range(len(indexList)):
            word = indexList[i]
            textDict = dict()
            textDict["word"] = word
            textDict["x"] = float(w2v_df["x"][word])
            textDict['y'] = float(w2v_df["y"][word])
            textDict['wcount'] = norm_dict[top_words[word]]
            textTSNEList.append(textDict)

        #print(textTSNEList)
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification+"word2vec 모델 만들기에 실패하였습니다. \n"+str(err))
        return "failed", "word2vec 모델 만들기에 실패하였습니다. 세부사항:" + str(e) 

    return True, textTSNEList

#word2vec('21800520@handong.edu', '북한', "2021-08-10T10:59:29.974Z", "20", 'word2vec')