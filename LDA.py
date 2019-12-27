from datetime import datetime
import esFunc
import time



def esGetDocs(sizeDoc):

    contents = []
    titles = []
    corpus = []

    ########################################################
    """
    파일이 있는 문서와 없는 문서가 있다.
    둘 다 elasticsearch에서 가지고 오고 싶으면 both = 1
    only Yes 첨부파일 : fileY = 1
    아니면 fileN = 0

    """
    ########################################################

    both = 0
    fileY = 0

    # dont touch this.
    fileN = 1

    if fileY == 1:
        fileN = 0
    else:
        fileN = 1

    if both == 1:
        fileY = 1
        fileN = 1


# 전처리
# 현재 상태 : 문서 뭉치 : [[제목,내용],[제목,내용],...]
# LDA작업은 문서의 내용을 가지고 하므로, 제목과 내용을 분리시켜야 한다.
# 제목을 다루는 array와 내용을 가지는 array을 따로 분리.
# 아랫 단에서 제목과 문서의 빈도 수를 묶을 때 제목을 다시 사용.

# 첨부파일이 없는 문서들
    if fileN == 1:
        result = esFunc.nkdbNoFile(sizeDoc)

        for oneDoc in result:
            oneDoc = oneDoc["_source"]
            
            if oneDoc["post_body"]:# 내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
                corpus.append(oneDoc["post_body"],(oneDoc["post_title"])
                # contents.append(oneDoc["post_body"])
                # titles.append((oneDoc["post_title"]))
                


# 첨부파일이 존재하는 문서들
    if fileY == 1:
        result = esFunc.nkdbFile(sizeDoc)

        # 전처리 2 for 첨부파일이 있는 데이터
        for oneDoc in result:
            oneDoc = oneDoc["_source"]
            
            if oneDoc["file_extracted_content"]:# 내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
                corpus.append(oneDoc["file_extracted_content"], oneDoc["post_title"]))
                # contents.append()
                # titles.append(()

    return corpus


################################################
"""
LDA 잠재 디리클레 할당
2019.12.27.
"""
def LDA():
    # time taken evaluation
    start = time.time()

    # variables
    NUM_DOC = 30
    NUM_TOPICS = 5
    NUM_ITER = 10
    # ES_INDEX = 'nkdboard'
    ES_INDEX = 'kolofoboard'

    # Phase 1 : ES에서 문서 쿼리 및 content와 title 분리 전처리


    # Query to ES New Version 191227
    # query whith does not have a filed "file_extracted_content"

    # titles = esGetDocs()[0]
    # contents = esGetDocs()[1]

    # esFunc.n?NoFile
    # results = es.search(index=ES_INDEX, body=doc)
    # result = results['hits']['hits']


    # query whith DOES have a filed "file_extracted_content"
    # 쿼리 내용 : 첨부파일 있는 문서들을 가져온다
    # doc = {
    #     'size': NUM_DOC,  # NUM_DOC/2,
    #     'query': {
    #         "exists": {
    #                 "field": "file_extracted_content"
    #             }
    #         # "bool": {
    #             #     "must_not": {
    #             #         "exists": {
    #             #             "field": "file_extracted_content"
    #             #         }

    #             #     }
    #             # }
    #         }
    #     }
    # results = es.search(index=ES_INDEX, body=doc)
    # result = results['hits']['hits']


# 전처리 2 for 첨부파일이 있는 데이터
    # for oneDoc in result:
    #     oneDoc = oneDoc["_source"]
    #     # 내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
    #     if oneDoc["file_extracted_content"]:
    #         contents.append(oneDoc["file_extracted_content"])
    #         titles.append((oneDoc["post_title"]))



# 알고리즘 정확성을 확인하기 위해 일부러 문서 순서를 섞는다.
    # Corpus
    Corpus = esGetDocs(2)
    print(type(Corpus))
    # for i in range(len(contents)):
    #     Corpus.append((titles[i], contents[i]))

    import random
    random.shuffle(Corpus)

    for i in range(len(contents)):
        titles[i] = Corpus[i][0]
        contents[i] = Corpus[i][1]
    # print(titles)#순서가 뒤바뀐 문서 set을 출력

    # print(len(contents))


# # phase 2 형태소 분석기

# # 형태소 분석기 instance
#     okt = Okt()

#     # colab에서 가져온 내용
#     # contents=[]
#     # title=[]
#     # for d in data:
#     #     if d[1]:#내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
#     #         contents.append(d[1])
#     #         title.append(d[0])

#     # con = [ con for con in contents if con]#내용이 비어 있는 빈문서 지우기. 해당 index을 구해서 제목에서 그 부분도 지워야 한다.
#     # print(len(contents))
#     # print(contents)

#     # print(title)
#     tokenized_doc = [okt.nouns(contents[cnt]) for cnt in range(len(contents))]
#     # print(tokenized_doc)
#     # len(tokenized_docㅡ
#     # len(tokenized_doc[0])

# # 한글자 단어들 지우기!
#     num_doc = len(tokenized_doc)
#     for i in range(num_doc):
#         tokenized_doc[i] = [word for word in tokenized_doc[i] if len(word) > 1]
#     # len(tokenized_doc)
#     # print(tokenized_doc)

# # LDA 알고리즘
#     from gensim import corpora
#     dictionary = corpora.Dictionary(tokenized_doc)
#     corpus = [dictionary.doc2bow(text) for text in tokenized_doc]

#     # print(len(corpus))
#     # print(corpus)
#     # print(dictionary[66])
#     # len(dictionary)

#     import gensim
#     ldamodel = gensim.models.ldamodel.LdaModel(
#         corpus, num_topics=NUM_TOPICS, id2word=dictionary, passes=NUM_ITER)
#     topics = ldamodel.print_topics(num_words=10)

#     # for topic in topics:
#     #     print(topic)
#     # print(ldamodel[corpus][0])

#     # LDA 결과 출력
#     for i, topic_list in enumerate(ldamodel[corpus]):
#         # if i == 5:
#             # break
#         print(i,'번째 문서의 topic 비율은',topic_list)
#     # topic_like : 문서 당 최대 경향 토픽만을 산출하기

#     topic_like = []
#     for i, topic_list in enumerate(ldamodel[corpus]):  # 문서 당 토픽 확률 분포 출력
#         # if i==5:
#             # break
#         print(i,'번째 문서의 최대 경향 topic',topic_list[0][0])
#         topic_like.append((i, topic_list[0][0]))
#     # print(topic_like)

#     # 같은 토픽 별로 정렬
#     topic_like = sorted(topic_like, key=itemgetter(1))
#     # print(topic_like)

#     # 같은 토픽에 있는 문서들을 정리
#     """
#     [
#         [//새로운 토픽
#             0,1,2,3,4//문서 01,2,3,4가 같은 토픽
#         ],
#         [
#             //새로운 토픽
#             5,6,7,8,9// 문서 5,6,7,8,9가 같은 토픽
#         ],
#         ...
#     ]
#     """
#     num_docs = len(topic_like)
#     idx = -1
#     sameTopicDocArr = []
#     for i in range(num_docs):
#         if idx != (topic_like[i][1]):  # 지금 보고 있는 문서번호가 새로운 주제 번호라면  새로운 토픽 종류 추가!
#             sameTopicDocArr.append([topic_like[i][0]])
#             idx = topic_like[i][1]  # 현재 관심있는 문서 번호 업데이트
#         else:
#             # 계속 보고 있던 주제라면 그대로 추가.
#             sameTopicDocArr[-1].append(topic_like[i][0])
#     # print(sameTopicDocArr)

# # 우선순위!
# # r같은 토픽에 있는 문서들의 내용을 묶어서 출력
# # contents는 문서들의 내용을 가지고 있다.
# # title은 문서의 제목을 가지고 있다.
#     # for topic in sameTopicDocArr:
#         # print("같은 주제들")
#         # for doc in topic:
#             # print(titles[doc])
#         # print("")

# # 동일한 주제에 있는 문서들의 내용을 묶어서 표현
#     # for topic in sameTopicDocArr:
#     # print("같은 주제들")
#     # for doc in topic:
#     #     print(contents[doc])
#     # print("")


# # 같은 토픽에 있는 문서들을 정리 + 문서의 제목과 함께 엮어서 pair으로 묶는다.
#     """
#     [
#         [//새로운 토픽
#             0,1,2,3,4//문서 01,2,3,4가 같은 토픽
#         ],
#         [
#             //새로운 토픽
#             5,6,7,8,9// 문서 5,6,7,8,9가 같은 토픽
#         ],
#         ...
#     ]
#     """

#     num_docs = len(topic_like)
#     idx = -1
#     sameTopicDocArrTitle = []
#     for i in range(num_docs):
#         docIndex = topic_like[i][0]
#         # 지금 보고 있는 문서번호가 관심 있는 주제에 속한다면, 같은 토픽에 추가! topic_like = [ (문서번호, 주제), (문서 번호, 주제),...]
#         if idx != (topic_like[i][1]):
#             # topic_like에서 i번째 문서의 번호
#             sameTopicDocArrTitle.append([(docIndex, titles[docIndex],tokenized_doc[docIndex])])
#             idx = topic_like[i][1]  # 현재 관심있는 문서 번호 업데이트
#         else:
#             # sameTopicDocArrTitle 맨 마지막에 새로운 문서번호로 추가!
#             sameTopicDocArrTitle[-1].append((docIndex, titles[docIndex],tokenized_doc[docIndex]))
#     # print(sameTopicDocArrTitle)

# # time taken evaluation
#     seconds = time.time() - start
#     m, s = divmod(seconds, 60)
#     h, m = divmod(m, 60)
#     print("투입된 문서의 수 : %d\n설정된 Iteratin 수 : %d\n설전된 토픽의 수 : %d" %(NUM_DOC, NUM_ITER, NUM_TOPICS))
#     print("%d 시간 : %02d 분 : %02d 초 " % (h, m, s))
#     # minuts = seconds / 60
#     # seconds = seconds % 2
#     # hours = minuts / 60
#     # minuts = minuts % 60
#     # print("time :", hours, " hours : ", minuts, " minutes : ", seconds, " seconds")
# # return
#     with open('../../handong/UniCenter/src/assets/special_first/data.json', 'w', -1, "utf-8") as f:
#         json.dump(sameTopicDocArrTitle, f, ensure_ascii=False)
#     print("documents topics: ")
#     """
#     코푸스의 길이 : 문서의 길이
#     for i in ldamodel.get_document_topics(corpus):
#         for j in i:
#             dictii[0]

#     """
#     list = []
#     for i in ldamodel.get_document_topics(corpus):
#         for j,k in enumerate(i):
#             if j > 5:
#                 break
#             list.append(dictionary.get(k[0]))
#         print(list)
#         list = []
#     # print(dictionary.get ( ldamodel.get_document_topics(corpus[8]) [0][0]))
#     # print("topic analysis: ")
#     # print(ldamodel.get_topic_terms(0))
#     print("show topics")
#     for i in ldamodel.show_topics():
#         print("documents ",i[0]," topics : ", i[1])
#     # print()
#     # return json.dumps(sameTopicDocArrTitle, ensure_ascii=False, indent=4)
#     return json.dumps("done", ensure_ascii=False, indent=4)
