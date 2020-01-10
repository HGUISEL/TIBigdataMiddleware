from datetime import datetime
from common import esFunc
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

def getTable(Numdoc):
    import gensim
    from gensim import corpora
    from gensim.models import TfidfModel
    from common import prs
    from common import cmm
    import numpy as np 
    from operator import itemgetter
    
    print(Numdoc,"개의 대량 문서 TF/IDF 분석")
    (docId, docTitle, tokenized_doc) = prs.readyData(Numdoc)
    print("형태소분석기 완료")
    cmm.showTime()

    #문서 가져옴 
    dct = corpora.Dictionary(tokenized_doc)
    #딕셔너리화
    print("딕셔너리 완료")
    cmm.showTime()

    corpus = corpus = [dct.doc2bow(line) for line in tokenized_doc]
    tfmodel = TfidfModel(corpus)
    #코퍼스에 담고 tfidf모델링
    sortEntire = []
    print("모델링 완료")
    cmm.showTime()
    
     
    #tf 값에 따라 정렬
    for id, topic_list in enumerate(tfmodel[corpus]):
        topic_list = sorted(topic_list, key=itemgetter(1), reverse = True) 
        sortEntire.append((id, topic_list))
    

    resultTF = []
    #i 는 int i = 0과 같은 역할    
    #index 는 문서번호가 나온다. 
    #section은 단어번호와 값의 쌍으로 나온다.
    for i, section in sortEntire:
        section = sortEntire[i]
        mainTF = []
        
        #print("\nㄱ===============================ㄴ")
        print(i, "번째 문서의 단어 수 : ", len(section[1]))

        for idx, (wordId, tfValue) in enumerate(section[1]):
            #print ("wordID : ", wordId, " tfValue : ",tfValue)
            mainTF.append((dct[wordId],tfValue))
            #if idx > 20:
            #    break
        #print(mainTF)
        #print("ㄷ===============================ㄹ\n")
        resultTF.append({"docID": docId[i], "docTitle": docTitle[i], "IFIDF": mainTF})
    

    cmm.showTime()
    #파일로 저장 
    DIR_FE = "../TIBigdataFE/src/assets/entire_tfidf/data.json"
    with open(DIR_FE, 'w', -1, "utf-8") as f:
            json.dump(resultTF, f, ensure_ascii=False)
    
    print("테이블 생성 완료")
    
    return resultTF
   
    
  


def getTFIDF(Numdoc):
    import gensim
    from gensim import corpora
    from gensim.models import TfidfModel
    from common import prs
    
    print("전처리 예시")
    #(docTitle, tokenized_doc)= prs.readyData(Numdoc) ##현재 5개 문서 호출 
    (docId, docTitle, tokenized_doc) = prs.readyData(Numdoc) #로 바뀔 예정 
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

    sortTF = []
    from operator import itemgetter
    for i, topic_list in enumerate(tfmodel[corpus]):
        topic_list = sorted(topic_list, key=itemgetter(1), reverse = True) 
       
        #print(i,'번째 문서의 TF/IDF 정렬',topic_list)
        sortTF.append((i, topic_list))

    #idf 값 깔끔하게 하는 용도 
    import numpy as np 

    resultTF = []
    #[n][1]을 하면 그 문서의 형태소 숫자를 알 수 있다.  
    ##현재 3번째 문서는 빈문서로 되어있음  유의

    print(sortTF)
    for i, section in sortTF:
        section = sortTF[i]
        mainTF = []
        print(i, "번째 문서의 단어 수 : ", len(section[1]))
        
        for wordid, value in section[1]:
            #print(dct[j],"-",np.around(value, decimals=5))
            mainTF.append((dct[wordid], np.around(value, decimals=5)))
        resultTF.append((i, mainTF))
        

    DIR_FE = "../TIBigdataFE/src/assets/homes_graph/data.json"
    with open(DIR_FE, 'w', -1, "utf-8") as f:
            json.dump(resultTF, f, ensure_ascii=False)

    return resultTF
    #return dct.token2id 



