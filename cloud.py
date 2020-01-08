from datetime import datetime
import esFunc
import time
from konlpy.tag import Okt
import json
import sys
import traceback
import gensim
import LDA

"""
    Wordcloud 생성 예제
    1. LDA.py의 dataPreprcs를 부른다
    2. dataPrePrcs를 사용하면 es에서 문서를 불러와 형태소 분석까지 수행
    3. gensim에서 tf/idf관련 api를 불러온다
"""


def test1():
    
    print("전처리 예시")
    sample1 = LDA.readyData()
    print("Data Ready End")
    num1 = LDA.loadData()
    print("전처리 분석 시작")
    tokenized_doc = LDA.dataPrePrcs()
    print("전처리 분석 완료")
    return tokenized_doc


"""
    test 1 에서 형태소 분석기를 거쳐 데이터를 가져오는것은 성공
"""


def test2():
    import gensim
    from gensim import corpora
    from gensim.models import TfidfModel
    
    print("전처리 예시")
    LDA.readyData()
    print("Data Ready End")
    #num1 = LDA.loadData()
    print("전처리 분석 시작")
    tokenized_doc = LDA.dataPrePrcs()
    print("전처리 분석 완료")

    #분리된 데이터를 dictionary화 
    dct = corpora.Dictionary(tokenized_doc)
    
    #코퍼스에 담음 
    corpus = [dct.doc2bow(line) for line in tokenized_doc]
    
    #tfidf 모델에 돌림
    tfmodel = TfidfModel(corpus)
    
    #벡터에 담음 
    vector = tfmodel[corpus[0]]

    #[(0, 0.004840388191324659), (1, 0.01275300075896571)... 의 형태 
    #print(vector)

    
    print(len(tokenized_doc))

    print("#################")

    sortTF = []
    from operator import itemgetter
    for i, topic_list in enumerate(tfmodel[corpus]):
        # if i == 5:
            # break
        topic_list = sorted(topic_list, key=itemgetter(1), reverse = True) 
        #print(i,'번째 문서의 TF/IDF 정렬',topic_list)
        sortTF.append((i, topic_list))


    mainTF = []
    resultTF = []
    #[n][1]을 하면 그 문서의 형태소 숫자를 알 수 있다.  
    ##현재 3번째 문서는 빈문서로 되어있음  유의
    for i, section in sortTF:
        section = sortTF[i]
        print(i, "번째 문서의 단어 수 : ", len(section[1]))
        for j, sec2 in section[1]:
            #print(dct[j],"-",sec2)
            mainTF.append((dct[j], sec2))
        resultTF.append((i, mainTF))

    
    DIR_FE = "../TIBigdataFE/src/assets/homes_graph/data.json"
    with open(DIR_FE, 'w', -1, "utf-8") as f:
            json.dump(resultTF, f, ensure_ascii=False)
    print(resultTF)
    

   



    return dct.token2id

