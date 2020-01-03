from datetime import datetime
import esFunc
import time
from konlpy.tag import Okt
import json
import sys
import traceback

# Frontend directory to store LDA result
DIR_FE = "../Front_KUBIC/src/assets/special_first/data.json"

 # global variables
NUM_DOC = 5
NUM_TOPICS = 3
NUM_ITER = 10
# ES_INDEX = 'nkdboard'
# ES_INDEX = 'kolofoboard'
titles = []
contents = []
start = None

def DBG(whatToBbg):
    print("\n\n\n\n#####DEBUG-MODE#####")
    print(whatToBbg)
    print("#####DEBUG-MODE#####\n\n\n\n")
    return 

# time taken evaluation
def showTime(start):
    seconds = time.time() - start
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    # print("투입된 문서의 수 : %d\n설정된 Iteratin 수 : %d\n설전된 토픽의 수 : %d" %(NUM_DOC, NUM_ITER, NUM_TOPICS))
    print("%d 시간 : %02d 분 : %02d 초 " % (h, m, s))
    # minuts = seconds / 60
    # seconds = seconds % 2
    # hours = minuts / 60
    # minuts = minuts % 60
    # print("time :", hours, " hours : ", minuts, " minutes : ", seconds, " seconds")

# Phase 1 : ES에서 문서 쿼리 및 content와 title 분리 전처리
def loadData():
    #if internet connection failed to backend    
    import json
    import sys
    import traceback
    global NUM_DOC
    try :
        # raise(Exception)
        corpus = esFunc.esGetDocs(NUM_DOC)
        print("connection to Backend server succeed!")
    except:
        traceback.print_exc()

        with open("./Datas/rawData.json", "rt", encoding="UTF8") as f:
            corpus = json.load(f)
        
        # DBG(len(corpus))
        NUM_DOC = len(corpus)
        print("connection to Backend server failed!")

    # 알고리즘 정확성을 확인하기 위해 일부러 문서 순서를 섞는다.
    import random
    random.shuffle(corpus)

    # titles = []
    # contents = []
    
    for idx, doc in enumerate(corpus):
        titles.append(doc[0])
        contents.append(doc[1])

    # print(titles)#순서가 뒤바뀐 문서 set을 출력
    print("문서 로드 완료!")
    print("투입된 문서의 수 : %d" %(NUM_DOC))
    # print(len(contents))

    return NUM_DOC

# phase 2 형태소 분석기 + 내용 없는 문서 지우기
def dataPrePrcs():
    
    # 형태소 분석기 instance
    okt = Okt()

    # colab에서 가져온 내용
    # contents=[]
    # title=[]
    # for d in data:
    #     if d[1]:#내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
    #         contents.append(d[1])
    #         title.append(d[0])

    # con = [ con for con in contents if con]#내용이 비어 있는 빈문서 지우기. 해당 index을 구해서 제목에서 그 부분도 지워야 한다.
    # print(len(contents))
    # print(contents)

    # print(title)
    tokenized_doc = [okt.nouns(contents[cnt]) for cnt in range(len(contents))]

    print("형태소 분석 완료!")
    print("투입된 문서의 수 : %d" %(NUM_DOC))
    showTime(start)

    # print(tokenized_doc)
    # len(tokenized_docㅡ
    # len(tokenized_doc[0])

    # 한글자 단어들 지우기!
    num_doc = len(tokenized_doc)
    for i in range(num_doc):
        tokenized_doc[i] = [word for word in tokenized_doc[i] if len(word) > 1]
    # len(tokenized_doc)
    # print(tokenized_doc)

    print("데이터 전처리 완료!")
    return tokenized_doc

def readyData():
    global NUM_DOC
    # Phase 1 : ES에서 문서 쿼리 및 content와 title 분리 전처리
    NUM_DOC = loadData()

    # phase 2 형태소 분석기 + 내용 없는 문서 지우기
    tokenized_doc = dataPrePrcs()
    return tokenized_doc

def runLda(tokenized_doc):  
    # LDA 알고리즘
    from gensim import corpora
    dictionary = corpora.Dictionary(tokenized_doc)#문서 별 각 단어에 고유 id 부여
    corpus = [dictionary.doc2bow(text) for text in tokenized_doc]# 문서를 벡터화?

    # print(len(corpus))
    # print(corpus)
    # print(dictionary[66])
    # len(dictionary)

    import gensim
    ldamodel = gensim.models.ldamodel.LdaModel(
        corpus, num_topics=NUM_TOPICS, id2word=dictionary, passes=NUM_ITER)
    topics = ldamodel.print_topics(num_words=10)

    for i, topic in topics:
        print(i,"번째 토픽을 구성하는 단어: ", topic)
    # print(ldamodel[corpus][0])

    # LDA 결과 출력
    for i, topic_list in enumerate(ldamodel[corpus]):
        # if i == 5:
            # break
        print(i,'번째 문서의 topic 비율은',topic_list)






    # topic_lkdhd : topic_likelyhood, 문서 당 최대 경향 토픽만을 산출하기
    # 같은 토픽 별로 정렬
    print()
    topic_lkdhd = []
    from operator import itemgetter
    for i, topic_list in enumerate(ldamodel[corpus]):
        # if i == 5:
            # break
        topic_list = sorted(topic_list, key=itemgetter(1), reverse = True) 
        # print(i,'번째 문서의 최대 경향 topic',topic_list[0][0])
        print(i,'번째 문서의 최대 경향 순서 topic 정렬',topic_list)
        topic_lkdhd.append((i, topic_list[0][0]))
        # print(i,'번째 문서의 topic 비율은',topic_list)
    # print(topic_lkdhd)

    # print()
    # for i, topic_list in enumerate(ldamodel[corpus]):  # 문서 당 토픽 확률 분포 출력
        # if i==5:
            # break
    # print(topic_lkdhd)
    # DBG(type(topic_lkdhd))

   

    # 최대 경향 토픽을 기준으로 같은 토픽에 있는 문서들을 정리
    """
    [
        [//새로운 토픽
            0,1,2,3,4//문서 01,2,3,4가 같은 토픽
        ],
        [
            //새로운 토픽
            5,6,7,8,9// 문서 5,6,7,8,9가 같은 토픽
        ],
        ...
    ]
    """
    # num_docs = len(topic_lkdhd)
    # idx = -1
    # sameTopicDocArr = []
    # for i in range(num_docs):
    #     if idx != (topic_lkdhd[i][1]):  # 지금 보고 있는 문서번호가 새로운 주제 번호라면  새로운 토픽 종류 추가!
    #         sameTopicDocArr.append([topic_lkdhd[i][0]])
    #         idx = topic_lkdhd[i][1]  # 현재 관심있는 문서 번호 업데이트
    #     else:
    #         # 계속 보고 있던 주제라면 그대로 추가.
    #         sameTopicDocArr[-1].append(topic_lkdhd[i][0])
    # # print(sameTopicDocArr)

    # 우선순위!
    # r같은 토픽에 있는 문서들의 내용을 묶어서 출력
    # contents는 문서들의 내용을 가지고 있다.
    # title은 문서의 제목을 가지고 있다.
        # for topic in sameTopicDocArr:
            # print("같은 주제들")
            # for doc in topic:
                # print(titles[doc])
            # print("")

    # 동일한 주제에 있는 문서들의 내용을 묶어서 표현
        # for topic in sameTopicDocArr:
        # print("같은 주제들")
        # for doc in topic:
        #     print(contents[doc])
        # print("")


    # tokenized_doc에는 개별 문서들의 단어들이 tokenized되어 저장되어 있다.



    # 같은 토픽에 있는 문서들을 정리 + 문서의 제목과 함께 엮어서 pair으로 묶는다.
    """
    [
        [//새로운 토픽
            0,1,2,3,4//문서 01,2,3,4가 같은 토픽
        ],
        [
            //새로운 토픽
            5,6,7,8,9// 문서 5,6,7,8,9가 같은 토픽
        ],
        ...
    ]
    """

    num_docs = len(topic_lkdhd)
    idx = -1
    sameTopicDocArrTitle = []
    for i in range(num_docs):
        docIndex = topic_lkdhd[i][0]
        # 지금 보고 있는 문서번호가 관심 있는 주제에 속한다면, 같은 토픽에 추가! topic_lkdhd = [ (문서번호, 주제), (문서 번호, 주제),...]
        if idx != (topic_lkdhd[i][1]):
            # topic_lkdhd에서 i번째 문서의 번호
            sameTopicDocArrTitle.append([(docIndex, titles[docIndex],tokenized_doc[docIndex])])
            idx = topic_lkdhd[i][1]  # 현재 관심있는 문서 번호 업데이트
        else:
            # sameTopicDocArrTitle 맨 마지막에 새로운 문서번호로 추가!
            sameTopicDocArrTitle[-1].append((docIndex, titles[docIndex],tokenized_doc[docIndex]))
    # print(sameTopicDocArrTitle)


# time taken evaluation
    seconds = time.time() - start
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print("투입된 문서의 수 : %d\n설정된 Iteratin 수 : %d\n설전된 토픽의 수 : %d" %(NUM_DOC, NUM_ITER, NUM_TOPICS))
    print("%d 시간 : %02d 분 : %02d 초 " % (h, m, s))
    # minuts = seconds / 60
    # seconds = seconds % 2
    # hours = minuts / 60
    # minuts = minuts % 60
    # print("time :", hours, " hours : ", minuts, " minutes : ", seconds, " seconds")
    
    
    with open(DIR_FE, 'w', -1, "utf-8") as f:
        json.dump(sameTopicDocArrTitle, f, ensure_ascii=False)
    # print("documents topics: ")
    """
    코푸스의 길이 : 문서의 길이
    for i in ldamodel.get_document_topics(corpus):
        for j in i:
            dictii[0]

    """
    # list = []
    # for i in ldamodel.get_document_topics(corpus):
    #     for j,k in enumerate(i):
    #         if j > 5:
    #             break
    #         list.append(dictionary.get(k[0]))
    #     print(list)
    #     list = []

    # print(dictionary.get ( ldamodel.get_document_topics(corpus[8]) [0][0]))
    # print("topic analysis: ")
    # print(ldamodel.get_topic_terms(0))
    print("\n")
    print("show topics")
    for i in ldamodel.show_topics():
        print("documents ",i[0]," topics : ", i[1])
    # print()
    # return json.dumps(sameTopicDocArrTitle, ensure_ascii=False, indent=4)
    # return json.dumps("done", ensure_ascii=False, indent=4)
    # return json.dump(sameTopicDocArrTitle, f, ensure_ascii=False)
    return sameTopicDocArrTitle


################################################
"""
LDA 잠재 디리클레 할당
2019.12.27.
"""

"""
function : LDA()
purpose : 자동으로 문서들을 주제들로 분류해준다.
input : num of documents, num of iteration, num of topics
output : 주제 별로 분류된 array
"""

def LDA(ndoc = NUM_DOC, nit = NUM_ITER, ntp = NUM_TOPICS):

    # change global value if get new params.
    global NUM_DOC
    global NUM_ITER
    global NUM_TOPICS

    if NUM_DOC != ndoc:
        NUM_DOC = ndoc 
    if NUM_ITER != nit:
        NUM_ITER = nit 
    if NUM_TOPICS != ntp:
        NUM_TOPICS = ntp 

    # time taken evaluation
    global start
    



    start = time.time()

    # # variables
    # NUM_DOC = 10
    # NUM_TOPICS = 5
    # NUM_ITER = 10
    # # ES_INDEX = 'nkdboard'
    # ES_INDEX = 'kolofoboard'


    titles = []
    contents = []
    # list에 새 값을 저장하지 않으면... 새로 할당하지 않으면... call by reference가 가능하다... 한번 생각해볼것.    

    # Phase 1 : ES에서 문서 쿼리 및 content와 title 분리 전처리
    # phase 2 형태소 분석기 + 내용 없는 문서 지우기
    tokenized_doc = readyData()
   
    # LDA 알고리즘
    result = runLda(tokenized_doc)

    print("Program Fin!")
    
    return result