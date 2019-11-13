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
        'size' : 10,
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
    results = es.search(index='kolofoboard', body=doc)
    result = results['hits']['hits']
    docArr=[]
    for oneDoc in result:
        oneDoc = oneDoc["_source"]
        docArr.append((oneDoc["post_title"],oneDoc["post_body"]))

#query whith DOES have a filed "file_extracted_content"
    doc = {
        'size' : 10,
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
    results = es.search(index='kolofoboard', body=doc)
    result = results['hits']['hits']
    for oneDoc in result:
        oneDoc = oneDoc["_source"]
        docArr.append((oneDoc["post_title"],oneDoc["file_extracted_content"]))

    # print(docArr)
    # results = results['hits']['hits'][2]["_source"]["post_body"]
    print(len(docArr))

    with open('file2.json', 'w', -1, "utf-8") as f:
        json.dump(docArr, f,ensure_ascii=False)
    with open('../../handong/UniCenter/src/assets/special_first/file2.json', 'w', -1, "utf-8") as f:
        json.dump(docArr, f,ensure_ascii=False)
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
    corpusArr=[]
    for i in result:
        corpusArr.append(i["_source"]["post_body"])

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
    result = results['hits']['hits']
    for i in result:
        corpusArr.append(i["_source"]["file_extracted_content"])
    #phase 2

    documents = [okt.nouns(corpusArr[cnt]) for cnt in range(len(corpusArr))]

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
            innerSumm.append(j)
        summ.append(innerSumm)
        innerSumm=[]

    with open('../../handong/UniCenter/src/assets/special_first/data.json', 'w', -1, "utf-8") as f:
        json.dump(arr, f,ensure_ascii=False)
    return json.dumps(arr, ensure_ascii=False, sort_keys = False, indent = 4)



    # return corpusArr

@app.route('/three', methods=['GET'])
def three():
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    okt = Okt()

    doc = {
        'size' : 10,
        'query': {
            'match_all' : {}
       }
    }
    results = es.search(index='nuacboard', body=doc,scroll='1m')
    # results = results['hits']['hits']
    # results = results['hits']['hits'][0]['_source']['file_extracted_content']
    # corpusArr=[]
    # for i in results:
        # if i == 1
            # results = i
        # corpusArr.append(i['_source'])
    
    return json.dumps(debug, ensure_ascii=False,indent = 4)
    # return jsonify(json.dumps(results, ensure_ascii=False))
    # response = Response(results,content_type="application/json; charset=utf-8" )
    # return response


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




