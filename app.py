from flask import Flask, jsonify, request, Response
from flask_restful import Resource, Api
from elasticsearch import Elasticsearch
from flask_cors import CORS, cross_origin
from konlpy.tag import Okt
from collections import Counter
from operator import itemgetter
import time
import json

# Sentence-tokenizer
import re

# Implement KR-Wordrank
from krwordrank.hangle import normalize
from krwordrank.word import KRWordRank

app = Flask(__name__)
# app.config['TESTING'] = True
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


# Url address of Elasticsearch
serverUrl = "http://203.252.103.86:8080"
# localUrl="http://localhost:9200"


# ElasticSearch connection
es = Elasticsearch(serverUrl)
app = Flask(__name__)
api = Api(app)


CORS(app, support_credentials=True)


@app.route("/hello")
def hello():
    contents = json.dumps("한글")
    return contents


#########################################
# 191227 ES Test update : use esFunc module
from common import esFunc
@app.route('/esTest', methods=['GET'])
def esTest():
    result = esFunc.esGetDocs(9)
    
    return json.dumps(result, ensure_ascii=False)



################################################
"""
LDA 잠재 디리클레 할당 모듈화
2019.12.27.
"""
################################################
# With LDA gensim library
import LDA
@app.route('/lda', methods=['GET'])
def three():
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    result = LDA.LDA(10)
    # print
    return json.dumps(result, ensure_ascii=False)

from elasticsearch import Elasticsearch
serverUrl = "http://203.252.103.86:8080"

es = Elasticsearch(serverUrl)


def textRank():
    import json
    DIR_FE = "../Front_KUBIC/src/assets/homes_graph/data.json"

    from konlpy.tag import Okt
    from gensim.summarization import keywords

    okt = Okt()

    with open("krWl.txt", "r" ,encoding='utf-8') as f:
        texts = f.read() 
        # print(f.read())
    tokenized_doc = okt.nouns(texts)
    tokenized_doc = ' '.join(tokenized_doc) 
    print("형태소 분석 이후 단어 토큰의 개수",len(tokenized_doc)) 

    result = keywords(tokenized_doc, words = 15 , scores=True)
    with open(DIR_FE, 'w', -1, "utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    return json.dumps(result, ensure_ascii=False)

def wordRank():
    #Retreive text from elasticsearch
    results = es.get(index='nkdb', doc_type='nkdb', id='5dc9fc5033ec463330e97e94')
    texts = json.dumps(results['_source'], ensure_ascii=False)

    # split the text by sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', texts)

    # normalize the text
    texts = [normalize(text, number=True) for text in sentences]

    wordrank_extractor = KRWordRank(
        min_count=3,  # Minimum frequency of word
        max_length=10,  # Maximum length of word
        verbose=True
    )

    beta = 0.85  # Decaying factor beta of PageRank
    max_iter = 10

    keywords, rank, graph = wordrank_extractor.extract(texts, beta, max_iter)

    result = []
    dic = {}
    # Make a dictionary [word, weight]
    for word, r in sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:30]:
        dic["y"] = r
        dic["label"] = word
        result.append(dic)
        dic = {}

    return json.dumps(result, ensure_ascii=False)
    # return result

@app.route('/wordrank', methods=['GET'])
def chseAlg():
    try: 
        result = wordRank()
    except:
        result =  textRank()
    return result
    
@app.route('/keywordGraph', methods=['POST', 'GET'])
@cross_origin(app)
def draw():
    if request.method == 'POST':
        result = request.json
        keyword = result["keyword"]

    wholeDataArr = []
    searchDataArr = []

    resultArr = []

    startYear = 1950
    offset = 10

    # From 1950 ~ 2020
    for i in range(0, 7):

        allDocs = {
            "query": {
                "bool": {
                    "must": {
                        "match_all": {}
                    },
                     "filter" : [
                    {"range" : {
                        "post_date" : {
                                "gte" : "1950-01||/M",
                                "lte" : "1950-01||/M",
                                "format": "yyyy-MM"
                            }
                        }}
                    ]
                }
            }
        }

     
        allDocs["query"]["bool"]["filter"][0]["range"]["post_date"]["gte"]= str(startYear+(i*offset))+"-01||/M"
        allDocs["query"]["bool"]["filter"][0]["range"]["post_date"]["lte"]= str(startYear+((i+1) *offset))+"-01||/M"

        res = es.search(index="nkdb", body=allDocs)
        numOfDocs = res["hits"]["total"]["value"]
        wholeDataArr.append(numOfDocs)
        print(numOfDocs)

        searchDocs = {
            "query" : {
                "bool" : {
                    "must" : [
                        {"match" : {"post_body" : ""}}
                    ],
                     "filter" : [
                    {"range" : {
                        "post_date" : {
                                "gte" : "1950-01||/M",
                                "lte" : "1950-01||/M",
                                "format": "yyyy-MM"
                            }
                        }}
                    ]
                }
            }
        }

        searchDocs["query"]["bool"]["filter"][0]["range"]["post_date"]["gte"]= str(startYear+(i*offset))+"-01||/M"
        searchDocs["query"]["bool"]["filter"][0]["range"]["post_date"]["lte"]= str(startYear+((i+1) *offset))+"-01||/M"
        searchDocs["query"]["bool"]["must"][0]["match"]["post_body"] = keyword

        res = es.search(index="nkdb", body=searchDocs)
        numOfDocs = res["hits"]["total"]["value"]
        searchDataArr.append(numOfDocs)

        print(numOfDocs)

    dic = {}
    resultWholeArr = []
    resultSearchArr = []
    # Angular Data Format{ y: 150, label: "Dec" }
    for i in range(0, 7):
        dic["y"] = wholeDataArr[i]
        dic["label"] = str(startYear+(i*offset))

        resultWholeArr.append(dic)
        dic = {}
        dic["y"] = searchDataArr[i]
        dic["label"] = str(startYear+(i*offset))
        resultSearchArr.append(dic)

        dic = {}

    resultArr.append(resultWholeArr)
    resultArr.append(resultSearchArr)

    print(resultArr)

    return json.dumps(resultArr, ensure_ascii=False)


@app.route('/test', methods=['POST', 'GET'])
def test():
    if request.method == 'POST':
        result = request.json
        keyword = result["keyword"]

    body = {
        "query": {
            "match_all": {}
        },
        "size": 1000,
    }

    res = es.search(index="nkdb", body=body)

    resultArr = res["hits"]["hits"]

    dateArr = []

    dayCntDic = {}

    for i in resultArr:
        dateArr.append(i["_source"]["post_date"])

    for i in dateArr:
        day = i[8:10]

        if day in dayCntDic:
            dayCntDic[day] += 1
        else:
            dayCntDic[day] = 1

    resultDic = []
    dic = {}

    for day, cnt in sorted(dayCntDic.items()):
        dic["y"] = cnt
        dic["label"] = day
        resultDic.append(dic)
        dic = {}

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

    # response.headers.add('Access-Control-Allow-Origin', '*')
    # response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


app.run(port=5000, debug=True)
