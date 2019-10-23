from datetime import datetime
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from elasticsearch import Elasticsearch
from flask_cors import CORS, cross_origin
import json


#Recognize Entity Name
from koalanlp import API
from koalanlp.proc import RoleLabeler
from koalanlp.proc import EntityRecognizer
from koalanlp.Util import initialize
from koalanlp.Util import finalize
from koalanlp import *


#Sentence-tokenizer
import re


#Implement TextRank Summarization
from gensim.summarization.summarizer import summarize
from newspaper import Article


#Implement KR-Wordrank 
from krwordrank.hangle import normalize
from krwordrank.word import KRWordRank




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

    print(resultArr)

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
