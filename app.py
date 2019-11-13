from datetime import datetime
from flask import Flask, jsonify, request, Response
from flask_restful import Resource, Api
from elasticsearch import Elasticsearch
from flask_cors import CORS, cross_origin
from  konlpy.tag import Okt
from collections import Counter
from operator import itemgetter
import random


import json

#Sentence-tokenizer
import re

#Implement KR-Wordrank 
from krwordrank.hangle import normalize
from krwordrank.word import KRWordRank

app = Flask(__name__)
# app.config['TESTING'] = True
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

K=10
V=0
document_topics = []
document_topic_counts = []
topic_word_counts = []
topic_counts = []
document_lengths = []

########################################

def p_topic_given_document(topic, d, alpha=0.1):
    return ((document_topic_counts[d][topic] + alpha) /
            (document_lengths[d] + K * alpha))

def p_word_given_topic(word, topic, beta=0.1):
    return ((topic_word_counts[topic][word] + beta) /
            (topic_counts[topic] + V * beta))

def topic_weight(d, word, k):
    return p_word_given_topic(word, k) * p_topic_given_document(k, d)

def choose_new_topic(d, word):
    return sample_from([topic_weight(d, word, k) for k in range(K)])

def sample_from(weights):
    total = sum(weights)
    rnd = total * random.random()
    for i, w in enumerate(weights):
        rnd -= w
        if rnd <= 0:
            return i
########################################



#Url address of Elasticsearch

serverUrl="http://203.252.103.86:8080"
# localUrl="http://localhost:9200"



#ElasticSearch connection
es=Elasticsearch(serverUrl)
app = Flask(__name__)
api = Api(app)



CORS(app, support_credentials=True)



@app.route("/hello")
def hello():
    contents = json.dumps("한글")
    return contents

@app.route('/one', methods=['GET'])
def one():
    results = es.get(index='nkdboard', doc_type='nkdboard', id='5db598c32cc6c120bac74bda')
    texts = json.dumps(results['_source'], ensure_ascii=False)
    return json.dumps(results, ensure_ascii=False)

#########################################
# 191112 ES Test
@app.route('/esTest', methods=['GET'])
def esTest():

    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    okt = Okt() 
#query whith does not have a filed "file_extracted_content"
    doc = {
        'size' : 20,
        'query': {
            # 'match_all' : {}
            # "exists":{
            #     "field" : "file_extracted_content"
            # },
            "bool": {
                "must_not": {
                    "exists": {
                        "field": "file_extracted_content"
                    }
                
                }
            }
       }
    }
    results = es.search(index='nkdboard', body=doc)
    result = results['hits']['hits']
    corpusContentArr=[]
    courpusArr=[]
    corpusTitleArr=[]
    for oneDoc in result:
        oneDoc = oneDoc["_source"]
        courpusArr.append((oneDoc["post_title"], oneDoc["post_body"]))
        # corpusContentArr.append(oneDoc["post_body"])
        # corpusTitleArr.append((oneDoc["post_title"]))

    with open('rawData.json', 'w', -1, "utf-8") as f:
        json.dump(courpusArr, f,ensure_ascii=False)
#query whith DOES have a filed "file_extracted_content"
    doc = {
        'size' : 20,
        'query': {
            "exists":{
                "field" : "file_extracted_content"
            }
            # "bool": {
            #     "must_not": {
            #         "exists": {
            #             "field": "file_extracted_content"
            #         }
                
            #     }
            # }
       }
    }
    results = es.search(index='nkdboard', body=doc)
    print(results)
    result = results['hits']['hits']

    # for oneDoc in result:
    #     oneDoc = oneDoc["_source"]
    #     corpusContentArr.append(oneDoc["file_extracted_content"])
    #     corpusTitleArr.append((oneDoc["post_title"]))
    
#    result_title_content = []
#    result_title_content.append(corpu)

   
    # with open('../../handong/UniCenter/src/assets/special_first/file2.json', 'w', -1, "utf-8") as f:
    #     json.dump(docArr, f,ensure_ascii=False)
    return json.dumps("download done! : ", ensure_ascii=False)

#########################################


@app.route('/two', methods=['GET'])
def two():

    #parameters
    num_size = 1000
    num_iter = 100



    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    okt = Okt() 

# Older Version
    # doc = {
    #     'size' : num_size,
    #     'query': {
    #         'match_all' : {}
    #    }
    # }
    # results = es.search(index='nkdboard', body=doc)
    
    # results = results['hits']['hits']
    # corpusArr=[]
    # for i in results:
    #     corpusArr.append(i['_source']['bodys'])

    # str(len(corpus))

#New Version 191112
#query whith does not have a filed "file_extracted_content"
    doc = {
        'size' : 20,
        'query': {
            # 'match_all' : {}
            # "exists":{
            #     "field" : "file_extracted_content"
            # },
            "bool": {
                "must_not": {
                    "exists": {
                        "field": "file_extracted_content"
                    }
                
                }
            }
       }
    }
    results = es.search(index='nkdboard', body=doc)
    result = results['hits']['hits']
    corpusContentArr=[]
    corpusTitleArr=[]
    for oneDoc in result:
        oneDoc = oneDoc["_source"]
        corpusContentArr.append(oneDoc["post_body"])
        corpusTitleArr.append((oneDoc["post_title"]))

#query whith DOES have a filed "file_extracted_content"
    doc = {
        'size' : 20,
        'query': {
            "exists":{
                "field" : "file_extracted_content"
            }
            # "bool": {
            #     "must_not": {
            #         "exists": {
            #             "field": "file_extracted_content"
            #         }
                
            #     }
            # }
       }
    }
    results = es.search(index='nkdboard', body=doc)
    print(results)
    result = results['hits']['hits']

    for oneDoc in result:
        oneDoc = oneDoc["_source"]
        corpusContentArr.append(oneDoc["file_extracted_content"])
        corpusTitleArr.append((oneDoc["post_title"]))
    
   

    #phase 2

    documents = [okt.nouns(corpusContentArr[cnt]) for cnt in range(len(corpusContentArr))]

    global document_topics
    global document_topic_counts
    global topic_word_counts
    global topic_counts
    global document_lengths
    global V
    
    #phase 3
    random.seed(0)
    document_topics = [[random.randrange(K) for word in document]
                        for document in documents]
    document_topic_counts = [Counter() for _ in documents]
    topic_word_counts = [Counter() for _ in range(K)]
    topic_counts = [0 for _ in range(K)]
    document_lengths = [len(document) for document in documents]
    distinct_words = set(word for document in documents for word in document)
    V = len(distinct_words)
    D = len(documents)

    for d in range(D):
        for word, topic in zip(documents[d], document_topics[d]):
            document_topic_counts[d][topic] += 1
            topic_word_counts[topic][word] += 1
            topic_counts[topic] += 1

    for iter in range(num_iter):
        for d in range(D):
            for i, (word, topic) in enumerate(zip(documents[d],document_topics[d])):
                document_topic_counts[d][topic] -= 1
                topic_word_counts[topic][word] -= 1
                topic_counts[topic] -= 1
                document_lengths[d] -= 1
                new_topic = choose_new_topic(d, word)
                document_topics[d][i] = new_topic
                document_topic_counts[d][new_topic] += 1
                topic_word_counts[new_topic][word] += 1
                topic_counts[new_topic] += 1
                document_lengths[d] += 1

    doc_top=[]
    for i in range(D):
        doc_top.append(document_topic_counts[i])

    tpl=[]
    for i in enumerate(document_topic_counts):
        tpl.append ((i[0],(i[1].most_common(1)[0][0])))
    tpl_s=sorted(tpl, key=itemgetter(1))

    idx = -1
    arr=[]
    for i in range(D):
        if idx != (tpl_s[i][1]):
            arr.append([tpl_s[i][0]])
            idx=tpl_s[i][1]
        else:
            arr[-1].append(tpl_s[i][0])

    
    summ = []
    innerSumm=[]
    for i in arr:
        for j in i:
            innerSumm.append((j,corpusTitleArr[j]))
        summ.append(innerSumm)
        innerSumm=[]
    
    with open('rawData.json', 'w', -1, "utf-8") as f:
        json.dump(result, f,ensure_ascii=False)
    with open('../../handong/UniCenter/src/assets/special_first/data.json', 'w', -1, "utf-8") as f:
        json.dump(summ, f,ensure_ascii=False)
    return json.dumps(summ, ensure_ascii=False, sort_keys = False, indent = 4)





################################################
"""
LDA 잠재 디리클레 할당
2019.11.14.
"""
################################################
#Three with LDA gensim library
@app.route('/three', methods=['GET'])
def three():
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    
#Phase 1 : ES에서 문서 쿼리 및 content와 title 분리 전처리


#Query to ES New Version 191112
#query whith does not have a filed "file_extracted_content"
#쿼리 내용: 첨부파일이 없는 문서들을 가지고 온다
    doc = {
        'size' : 20,
        'query': {
            # 'match_all' : {}
            # "exists":{
            #     "field" : "file_extracted_content"
            # },
            "bool": {
                "must_not": {
                    "exists": {
                        "field": "file_extracted_content"
                    }
                
                }
            }
       }
    }
    results = es.search(index='nkdboard', body=doc)
    result = results['hits']['hits']
    
#전처리
#현재 상태 : [[제목,내용],[제목,내용],...]
#LDA작업은 문서의 내용을 가지고 하므로, 제목과 내용을 분리시켜야 한다.
#제목을 다루는 array와 내용을 가지는 array을 따로 분리.
##아랫 단에서 제목과 문서의 빈도 수를 묶을 때 제목을 다시 사용.
    contents=[]
    titles=[]

    for oneDoc in result:
        oneDoc = oneDoc["_source"]
        if oneDoc["post_body"]:#내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
            contents.append(oneDoc["post_body"])
            titles.append((oneDoc["post_title"]))

#query whith DOES have a filed "file_extracted_content"
#쿼리 내용 : 첨부파일 있는 문서들을 가져온다
    doc = {
        'size' : 20,
        'query': {
            "exists":{
                "field" : "file_extracted_content"
            }
            # "bool": {
            #     "must_not": {
            #         "exists": {
            #             "field": "file_extracted_content"
            #         }
                
            #     }
            # }
       }
    }
    results = es.search(index='nkdboard', body=doc)
    result = results['hits']['hits']


#전처리 2 for 첨부파일이 있는 데이터
    for oneDoc in result:
        oneDoc = oneDoc["_source"]
        if oneDoc["file_extracted_content"]:#내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
            contents.append(oneDoc["file_extracted_content"])
            titles.append((oneDoc["post_title"]))
    
    # print(titles)
    # print(contents)

#phase 2 형태소 분석기

#형태소 분석기 instance
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
    # print(tokenized_doc)
    # len(tokenized_docㅡ
    # len(tokenized_doc[0])

#한글자 단어들 지우기!
    num_doc = len(tokenized_doc)
    for i in range(num_doc):
        tokenized_doc[i]=[word for word in tokenized_doc[i] if len(word) > 1]
    # len(tokenized_doc)
    # print(tokenized_doc)

# LDA 알고리즘
    from gensim import corpora
    dictionary = corpora.Dictionary(tokenized_doc)
    corpus = [dictionary.doc2bow(text) for text in tokenized_doc]

    # print(len(corpus))
    # print(corpus)
    # print(dictionary[66])
    # len(dictionary)
 
    import gensim
    NUM_TOPICS = 5
    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics = NUM_TOPICS, id2word=dictionary, passes=15)
    topics = ldamodel.print_topics(num_words=10)
    
    # for topic in topics:
    #     print(topic)
    # print(ldamodel[corpus][0])



    #LDA 결과 출력
    for i, topic_list in enumerate(ldamodel[corpus]):
        if i==5:
            break
        print(i,'번째 문서의 topic 비율은',topic_list)
    #topic_like : 문서 당 최대 경향 토픽만을 산출하기

    topic_like=[]
    for i, topic_list in enumerate(ldamodel[corpus]): # 문서 당 토픽 확률 분포 출력
        # if i==5:
            # break
        # print(i,'번째 문서의 최대 경향 topic',topic_list[0][0])
        topic_like.append((i,topic_list[0][0]))
    # print(topic_like)

    #같은 토픽 별로 정렬
    topic_like = sorted(topic_like, key=itemgetter(1))
    # print(topic_like)

    #같은 토픽에 있는 문서들을 정리
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
    num_docs = len(topic_like)
    idx = -1
    sameTopicDocArr=[]
    for i in range(num_docs):
        if idx != (topic_like[i][1]):#지금 보고 있는 문서번호가 새로운 주제 번호라면  새로운 토픽 종류 추가!
            sameTopicDocArr.append([topic_like[i][0]])
            idx=topic_like[i][1] # 현재 관심있는 문서 번호 업데이트
        else:
            sameTopicDocArr[-1].append(topic_like[i][0])#계속 보고 있던 주제라면 그대로 추가.
    # print(sameTopicDocArr)

#r같은 토픽에 있는 문서들의 내용을 묶어서 출력
#contents는 문서들의 내용을 가지고 있다.
#title은 문서의 제목을 가지고 있다.
    for topic in sameTopicDocArr:
        print("같은 주제들")
        for doc in topic:
            print(titles[doc])
        print("")

#동일한 주제에 있는 문서들의 내용을 묶어서 표현
    # for topic in sameTopicDocArr:
    # print("같은 주제들")
    # for doc in topic:
    #     print(contents[doc])
    # print("")





#같은 토픽에 있는 문서들을 정리 + 문서의 제목과 함께 엮어서 pair으로 묶는다.
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
    
    num_docs = len(topic_like)
    idx = -1
    sameTopicDocArrTitle=[]
    for i in range(num_docs):
        docIndex = topic_like[i][0]
        if idx != (topic_like[i][1]):#지금 보고 있는 문서번호가 관심 있는 주제에 속한다면, 같은 토픽에 추가! topic_like = [ (문서번호, 주제), (문서 번호, 주제),...]
            sameTopicDocArrTitle.append([(docIndex,titles[docIndex])])#topic_like에서 i번째 문서의 번호
            idx=topic_like[i][1] # 현재 관심있는 문서 번호 업데이트
        else:
            sameTopicDocArrTitle[-1].append((docIndex,titles[docIndex]))#sameTopicDocArrTitle 맨 마지막에 새로운 문서번호로 추가!
    # print(sameTopicDocArrTitle)
        

# return
    with open('../../handong/UniCenter/src/assets/special_first/data.json', 'w', -1, "utf-8") as f:
        json.dump(sameTopicDocArrTitle, f,ensure_ascii=False)
    return json.dumps(sameTopicDocArrTitle, ensure_ascii=False,indent = 4)

@app.route('/wordrank', methods=['GET'])
def wordRank():

    #Retreive text from elasticsearch
    results = es.get(index='crawling', doc_type='nkdboard', id='5d76f149a2e5d0edebd8522f')
    texts = json.dumps(results['_source'], ensure_ascii=False)
    
    # #split the text by sentences
    # sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', texts)
    

    # #normalize the text
    # texts = [normalize(text, number=True) for text in sentences]
    
    # wordrank_extractor = KRWordRank(
    #     min_count = 7,  # Minimum frequency of word
    #     max_length=10,  # Maximum length of word
    #     verbose = True
    # )

    # beta = 0.85  # Decaying factor beta of PageRank
    # max_iter = 10
  
    # keywords, rank, graph = wordrank_extractor.extract(texts, beta, max_iter)
    
    # result=[]
    # dic={}
    # #Make a dictionary [word, weight]
    # for word, r in sorted(keywords.items(), key=lambda x:x[1], reverse=True)[:30]:
    #     dic["y"]=r
    #     dic["label"]=word
    #     result.append(dic)
    #     dic={}

    return json.dumps(results, ensure_ascii=False)



# # @app.route('/ext', methods=['GET'])
# # def extractEntity():
    
    
# #     # ETRI API KEY
# #     API_KEY = '2aca8d0f-ccdb-4074-ba54-de2b3c2a7bec'
# #      #Retreive text from elasticsearch
# #     results = es.get(index='text', doc_type='text', id='1')
# #     texts = json.dumps(results['_source']["attachment"]["content"], ensure_ascii=False)

# #     recognizer = EntityRecognizer(API.ETRI, API_KEY)

# #     parsed = recognizer.analyze("안녕하세요 문재인입니다. 하늘에 계신 우리아버지여.")
    
# #     print(parsed)
# #     for entity in parsed[0].getEntities():
# #         print(entity)




# #     return "Good"


# @app.route('/term')
# def term():
#     finalize()
#     return "Terminated"


# @app.route('/', methods=['GET'])
# def index():
#     results = es.get(index='text', doc_type='text', id='1')
   
#     return json.dumps(results['_source'], ensure_ascii=False)

# @app.route('/search', methods=['POST', 'GET'])
# def search():
    
#     keyword=request.json["keyword"]
#     body= {
#         "query" : {
#             "match_all":{
                
#             }
#         }
#     }

#     res = es.search(index="text", body=body)

#     return json.dumps(res["hits"]["hits"], ensure_ascii=False)



@app.route('/test', methods=['POST', 'GET'])
def test():
    if request.method=='POST':
       result=request.json 
       keyword=result["keyword"]


    body = {
        "query" : {
            "match_all" : {}
        },
        "size" : 1000,
    }
    
    res= es.search(index="crawling", body=body)

    resultArr = res["hits"]["hits"]

    dateArr=[]

    dayCntDic={}


    for i in resultArr:
        dateArr.append(i["_source"]["dates"])

    
    for i in dateArr:
        day=i[8:10]
        
        if day in dayCntDic:
            dayCntDic[day] +=1
        else:
            dayCntDic[day] =1


    resultDic=[]
    dic={}

    for day, cnt in sorted(dayCntDic.items()):
        dic["y"]=cnt
        dic["label"]=day
        resultDic.append(dic)
        dic={}


    return json.dumps(resultDic, ensure_ascii=False)
 



# def rank(contents):
#      #split the text by sentences
#     sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', contents)
    

#     #normalize the text
#     contents = [normalize(text, number=True) for text in sentences]
    
#     wordrank_extractor = KRWordRank(
#         min_count = 7,  # Minimum frequency of word
#         max_length=10,  # Maximum length of word
#         verbose = True
#     )

#     beta = 0.85  # Decaying factor beta of PageRank
#     max_iter = 10
  
#     keywords, rank, graph = wordrank_extractor.extract(contents, beta, max_iter)
    
#     result=[]
#     dic={}
#     #Make a dictionary [word, weight]
#     for word, r in sorted(keywords.items(), key=lambda x:x[1], reverse=True)[:30]:
#         dic["y"]=r
#         dic["label"]=word
#         result.append(dic)
#         dic={}
    
#     return result

@app.after_request
def after_request(response):
    
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

app.run(port=5000, debug=True)




