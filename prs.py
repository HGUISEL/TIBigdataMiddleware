# KUBIC module : prs.py
# created Data : 오늘 :)
# purpose : 데이터 전처리 모듈
import traceback
# from datetime import datetime
import esFunc
import time
from konlpy.tag import Okt

#RANDOM_MODE
# 알고리즘 정확성 확인을 위해서 문서를 불러와서 순서를 섞는다.
RANDOM_MODE = False

#OFFLINE_MODE
# use sample data in ./raw data sample, and not connet to ES.
# without HGU-WLAN network, use raw data sample no matter this value
BACKEND_CONCT = True

 # global variables
NUM_DOC = 5
titles = []
contents = []
start = None
# ES_INDEX = 'nkdboard'
# ES_INDEX = 'kolofoboard'

# Sample Raw Data from Backend directory
DIR_SMP_DATA = "./raw data sample/rawData.json"

# time taken evaluation
def showTime():
    global start
    seconds = time.time() - start
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    # print("투입된 문서의 수 : %d\n설정된 Iteratin 수 : %d\n설전된 토픽의 수 : %d" %(NUM_DOC, NUM_ITER, NUM_TOPICS))
    print("%d 시간 : %02d 분 : %02d 초 " % (h, m, s))

# Phase 1 : ES에서 문서 쿼리 및 content와 title 분리 전처리
def loadData():
    #if internet connection failed to backend    
    import json
    import sys
    import traceback
    global NUM_DOC
    print("데이터 로드 중...")
    try :
        if BACKEND_CONCT == False:
            raise Exception("서버 연결 불가")
        corpus = esFunc.esGetDocs(NUM_DOC)
        print("connection to Backend server succeed!")
        print(len(corpus),"개의 문서를 가져옴")# 문서의 수... 내용 없으면 뺀다...

    except Exception as e:
        # traceback.print_exc()
        print('Error: {}. {}'.format(sys.exc_info()[0],
                sys.exc_info()[1]))
        print("대체 파일 로드 from ",DIR_SMP_DATA)

        with open(DIR_SMP_DATA, "rt", encoding="UTF8") as f:
            corpus = json.load(f)
        
        print("connection to Backend server failed!")
    showTime() 
    NUM_DOC = len(corpus) # 전체 사용 가능한 문서 수를 업데이트한다. 
    print("문서 로드 완료!")
    print()


    # 알고리즘 정확성을 확인하기 위해 일부러 문서 순서를 섞는다.
    if RANDOM_MODE == True:
        import random
        random.shuffle(corpus)

    count = 0
    for idx, doc in enumerate(corpus):
        # print(doc["content"])
        if doc["content"] != "":
            titles.append(doc["post_title"])
            contents.append(doc["content"])
        else:
            count += 1

    num_doc = len(contents)
    print(count,"개의 문서가 내용이 없음")
    # print(titles)#순서가 뒤바뀐 문서 set을 출력
    print("투입된 문서의 수 : %d" %(num_doc))
    # print(len(contents))

    # update NUM_DOC
    return num_doc

# phase 2 형태소 분석기 + 내용 없는 문서 지우기
def dataPrePrcs():
    
    # 형태소 분석기 instance
    okt = Okt()
    print("데이터 전처리 중... It may takes few hours...")
    tokenized_doc = [okt.nouns(contents[cnt]) for cnt in range(len(contents))]

    print("형태소 분석 완료!")
    print("투입된 문서의 수 : %d" %(NUM_DOC))
    showTime()

    # 한글자 단어들 지우기!
    num_doc = len(tokenized_doc)
    for i in range(num_doc):
        tokenized_doc[i] = [word for word in tokenized_doc[i] if len(word) > 1]

    print("데이터 전처리 완료!")
    return tokenized_doc


"""
# functin : readData
# purpose : 
# input : 
# output : 
"""
def readyData(num_doc = NUM_DOC):

    # time taken evaluation
    global start
    start = time.time()

    # NUM_DOC initialize
    global NUM_DOC
    if num_doc != NUM_DOC:
        NUM_DOC = num_doc

    # Phase 1 : ES에서 문서 쿼리 및 content와 title 분리 전처리
    print("\n\n#####Phase 1-1 : 데이터 로드 실행#####")
    NUM_DOC = loadData()# load data and update NUM_DOC

    # phase 2 형태소 분석기 + 내용 없는 문서 지우기
    print("\n\n#####Phase 1-2 : 데이터 전처리 실행#####")
    tokenized_doc = dataPrePrcs()
    return tokenized_doc