#-*- coding:utf-8 -*-
from flask import Flask, jsonify, request, Response
from flask_restful import Resource, Api
from elasticsearch import Elasticsearch
from flask_cors import CORS, cross_origin
from collections import Counter
from operator import itemgetter
import time
import json
import sys
from rcmdHelper import rcmd as rc

import os
if os.name == "nt":
    from eunjeon import Mecab
else:
    from konlpy.tag import Mecab
print("os system : ", os.name)

sys.path.insert(0, './common')

# Sentence-tokenizer
import re
import tfidf
# Implement KR-Wordrank
from krwordrank.hangle import normalize
from krwordrank.word import KRWordRank

app = Flask(__name__)#flask 객체를 app에 할당
# app.config['TESTING'] = True
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


# Url address of Elasticsearch
import socket
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

serverUrl = get_ip_address()  # '192.168.0.110'
if(serverUrl != "http://203.252.112.15:9200"):
    serverUrl="http://localhost:9200"
else:
    serverUrl = "http://203.252.112.14:9200"

# ElasticSearch connection
es = Elasticsearch(serverUrl)
app = Flask(__name__)
api = Api(app)


CORS(app, support_credentials=True)


@app.route("/hello",methods=['GET'])
def hello():
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    contents = "ndllocvcv"

    from konlpy.tag import Mecab
    tagger = Mecab()
    t = tagger.pos("고양이는 양옹뉴턴야옹")
    print("========================================")
    return json.dumps(t, ensure_ascii=False)
#
#
#
#@app.route("/tfidfRaw",methods=['GET'])
#def tfidfRaw():
#    app = Flask(__name__)
#    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
#
#    Numdoc = 600
#
#    contents = tfidf.getTfidfRaw(Numdoc)
#    #return json.dumps(contents, ensure_ascii=False)
#    return json.dumps(contents, ensure_ascii=False)
#
#@app.route("/tfidfTable",methods=['GET'])
#def tfidfTable():
#    app = Flask(__name__)
#    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
#
#    Numdoc = 600
#
#    contents = tfidf.getTfidfTable(Numdoc)
#    #return json.dumps(contents, ensure_ascii=False)
#    return json.dumps(contents, ensure_ascii=False)
#
##########################################
## 191227 ES Test update : use esFunc module
#from common import esFunc
#@app.route('/esTest', methods=['GET'])
#def esTest():
#    result = esFunc.esGetDocs(9)
#    
#    return json.dumps(result, ensure_ascii=False)
#
#
#
#################################################
#"""
#LDA 잠재 디리클레 할당 모듈화
#2019.12.27.
#"""
#################################################
## With LDA gensim library
#
#import LDA
#@app.route('/lda', methods=['GET'])
#def lda():
#    app = Flask(__name__)
#    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
#    
#    result = LDA.LDA(10) ##문서 10개 돌림 
#    # print
#    return json.dumps(result, ensure_ascii=False)
#
#################################################
#"""
#SVM
#2020.9.24.
#"""
#################################################
## With LDA gensim library

import SVM
@app.route('/svm', methods=['GET'])#app객체로 라우팅 경로 설정
def svm():
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    svm_result = SVM.SVM(10) ##문서 10개 돌림 
    print(svm_result)
    return json.dumps(svm_result, ensure_ascii=False)


##recomandation function
#@app.route('/rcmd', methods=['GET', 'POST'])
#def rcmd():
#    print("recomandation function init.")
#
#    if request.method == 'POST':
#        req = request.json
#        idList = req["idList"]
#
#    # print("Get id list from Front-End: ",idList)
#
#    rcmdList = rc.getRcmd(idList)
#    print("rcmd function done!")
#    
#    return json.dumps(rcmdList, ensure_ascii=False)
#
#
#
#def textRank():
#    import json
#    from gensim.summarization import keywords
#    DIR_FE = "../Front_KUBIC/src/assets/special_first/ctgRNNResult.json"
#
#    with open(DIF_FE,'r',encoding='utf-8') as fp:
#        data = json.load(fp)
#
#    corpus = data[0]["doc"]
#
#
#    isTokened = True
#
#    if isTokened == True:
#        tokenized_doc = []
#        for doc in corpus:
#            tokenized_doc.append(doc["words"])
#    else:
#        contents = []
#        for doc in corpus:
#            contents.append(doc["contents"])
#
#        tagger = Mecab()
#        print("데이터 전처리 중... It may takes few hours...")
#        tokenized_doc = [tagger.nouns(contents[cnt]) for cnt in range(len(contents))]
#
#    # texts = """
#    # □ 평화번영을 위한 남북관계 발전방안「6.15공동선언」 이후 남북관계는 빠른 속도로 발전하고 있습니다. 그러나 장기간에 걸친 분단으로 인해 냉전적 사고와 논리, 불신이 남과 북의 관계 진전에 발목을 잡고 있는 것도 사실입니다.공존공영의 남북관계를 정립하기 위해서는 무엇보다 상호신뢰를 쌓기 위한 노력과, 이를 뒷받침할 수 있는 통일교육 지원 등의 국내적 기반 조성도 필요합니다.우리 민주평화통일자문회의 위원들은 한반도의 평화번영을 위한 남북관계의 발전을 위해 다음의 건의를 드립니다.첫 째, 남과 북이 서로 만날 수 있는 기회를 많이 만들어내야 합니다.대구 유니버시아드대회를 통해 우리는 북한 주민들이 우리와 얼마나 다른 사고와 행동을 하는지 생생히 보았습니다.남과 북이 서로를 이해하고 화합하기 위해서는 무엇보다 먼저 많이 만나는 것이 필요합니다.둘 째, 지방자치단체와 시민사회단체 등의 남북교류가 활성화되어야 합니다.남북한 관계가 탄탄한 뿌리를 내리기 위해서는 남과 북을 잇는 다양한 네트워크가 필요합니다. 먼저 지방자치단체간 자매결연을 통한 협력체제를 구축하고, 시민사회단체간에도 연대를 맺는 활동이 필요합니다.이들 상호간의 남북교류는 안정적인 남북관계를 뒷받침하는 든든한 버팀목이 될 수 있을 것입니다.셋 째, 인도주의적 대북지원이 적극적으로 확대되어야 합니다.인도주의 정신에 입각한 대북지원은 정치적 논리를 초월하여 실천해야 할 매우 중요한 과제입니다. 일회성 지원이나 이벤트성 행사보다는 지속적인 지원이 절실히 필요합니다.범국민적 차원에서 폭넓게 펼칠 수 있는 북한에 나무심기 운동, 북한 어린이 돕기운동 등이 좋은 예가 될 수 있을 것입니다.넷 째, 제2차 남북정상회담이 빠른 시일 내에 열리기를 기대합니다.북핵문제 해결 등 한반도의 평화체제 구축을 위한 역사적 전기 마련이 필요한 시점입니다.제2차 정상회담을 통해 보다 밝은 남북관계를 재정립하고, 동북아의 안정에도 기여할 수 있을 것입니다.□ 국민통합과 한민족 통일역량 결집방안한반도에서의 평화와 번영의 성취는 동북아뿐만 아니라 전세계의 평화와 번영에도 긴요하다는 점에서 하루빨리 이루어야 할 민족적 과제입니다. 따라서 7천만 국내외 동포의 통일역량의 결집은 장차 한반도 통일에 결정적 담보가 될 것 입니다.해외동포는 통일을 위한 가교의 역할로, 남북한 주민은 서로를 이해하는 넓은 아량으로 그리고 우리 사회 내부는 겨레가 함께 살아갈 수 있는 의지를 모아 새로운 시대에 새로운 한민족 공동체를 창조하는 데 적극적으로 참여하여야 합니다.우리 민주평화통일자문회의 위원들은 국민대통합과 한민족의 통일역량 결집을 위해 다음의 건의를 드립니다.첫 째, 분단의 결과로 생긴 민족내부의 차이와 갈등을 폭넓게 수용하는 정책이 필요합니다.냉전적 사고에 사로잡힌 불신과 대결로는 민족의 통일역량을 결집할 수 없습니다. 다양한 의견과 차이를 인정하고 이를 공존의 기초로 받아들이는 포용의 자세가 필요합니다.국내는 물론 현지사회에 동화된 한민족의 일원도 차이와 갈등을 넓게 아우르는 민족대통합의 정책이 필요합니다.둘 째, 한민족 경제·문화 공동체를 만들어 민족상생의 시대를 열어야 합니다.세계화 시대에 각 나라에 거주하는 해외동포들이 경제·사회적으로 주류에 서서 한민족의 정체성을 유지할 수 있도록, 그리고 현지 국민들과 융화하면서 자긍심을 유지·발전시킬 수 있도록 지원해야 합니다.한민족 경제·문화공동체를 형성하기 위해 현지 한국어 교육의 강화, 청년세대의 상호 교류, 지역사회내의 다양한 네트워크 형성으로 한민족의 정체성을 강화하여야 합니다.또한 현지 국민들과의 융화를 위해 이미 설립되어 있거나 설립해야 할 「한국 문화센터」에 지원을 아끼지 말아야 합니다.셋 째, 민주평통 해외자문위원의 역할을 강화할 필요가 있습니다.동북아 중심국가로 성장하는 통일한국의 건설에는 국민대통합과 함께 해외동포의 역량결집이 대단히 중요합니다. 특히 한민족의 10% 이상인 7백만이 해외에 살고 있다는 점은 큰 자산이라 할 수 있습니다.해외동포의 통일역량을 효과적으로 결집하는 데 민주평통 해외위원의 참여와 역할이 대단히 중요한 비중을 차지하고 있습니다. 이를 위한 제도적 장치가 시급히 마련되어야 합니다.
#    # """
#
#    # with open("krWl.txt", "r" ,encoding='utf-8') as f:
#    #     texts = f.read() 
#        # print(f.read())
#        # tokenized_doc = tagger.nouns(texts)
#        # tokenized_doc = ' '.join(tokenized_doc) 
#        # print("형태소 분석 이후 단어 토큰의 개수",len(tokenized_doc)) 
#
#    result = keywords(tokenized_doc, words = 15 , scores=True)
#    # with open(DIR_FE, 'w', -1, "utf-8") as f:
#    with open("./wrCul.json", 'w', -1, "utf-8") as f:
#        json.dump(result, f, ensure_ascii=False)
#
#    return json.dumps(result, ensure_ascii=False)
#
#def wordRank():
#    #Retreive text from elasticsearch
#    results = es.get(index='nkdb', doc_type='nkdb', id='5dc9fc5033ec463330e97e94')
#    texts = json.dumps(results['_source'], ensure_ascii=False)
#
#    # split the text by sentences
#    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', texts)
#
#    # normalize the text
#    texts = [normalize(text, number=True) for text in sentences]
#
#    wordrank_extractor = KRWordRank(
#        min_count=3,  # Minimum frequency of word
#        max_length=10,  # Maximum length of word
#        verbose=True
#    )
#
#    beta = 0.85  # Decaying factor beta of PageRank
#    max_iter = 10
#
#    keywords, rank, graph = wordrank_extractor.extract(texts, beta, max_iter)
#
#    result = []
#    dic = {}
#    # Make a dictionary [word, weight]
#    for word, r in sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:30]:
#        dic["y"] = r
#        dic["label"] = word
#        result.append(dic)
#        dic = {}
#
#    return json.dumps(result, ensure_ascii=False)
#    # return result
#
#@app.route('/wordrank', methods=['GET'])
#def chseAlg():
#    try: 
#        result = wordRank()
#    except:
#        result =  textRank()
#    return result
#    
#@app.route('/keywordGraph', methods=['POST', 'GET'])
#@cross_origin(app)
#def draw():
#    if request.method == 'POST':
#        result = request.json
#        keyword = result["keyword"]
#
#    wholeDataArr = []
#    searchDataArr = []
#
#    resultArr = []
#
#    startYear = 1950
#    offset = 10
#
#    # From 1950 ~ 2020
#    for i in range(0, 8):
#
#        allDocs = {
#            "query": {
#                "bool": {
#                    "must": {
#                        "match_all": {}
#                    },
#                     "filter" : [
#                    {"range" : {
#                        "post_date" : {
#                                "gte" : "1950-01||/M",
#                                "lte" : "1950-01||/M",
#                                "format": "yyyy-MM"
#                            }
#                        }}
#                    ]
#                }
#            }
#        }
#
#     
#        allDocs["query"]["bool"]["filter"][0]["range"]["post_date"]["gte"]= str(startYear+(i*offset))+"-01||/M"
#        allDocs["query"]["bool"]["filter"][0]["range"]["post_date"]["lte"]= str(startYear+((i+1) *offset))+"-01||/M"
#
#        res = es.search(index="nkdb", body=allDocs)
#        numOfDocs = res["hits"]["total"]["value"]
#        wholeDataArr.append(numOfDocs)
#        print(numOfDocs)
#
#        searchDocs = {
#            "query" : {
#                "bool" : {
#                    "must" : [
#                        {"match" : {"post_body" : ""}}
#                    ],
#                     "filter" : [
#                    {"range" : {
#                        "post_date" : {
#                                "gte" : "1950-01||/M",
#                                "lte" : "1950-01||/M",
#                                "format": "yyyy-MM"
#                            }
#                        }}
#                    ]
#                }
#            }
#        }
#
#        searchDocs["query"]["bool"]["filter"][0]["range"]["post_date"]["gte"]= str(startYear+(i*offset))+"-01||/M"
#        searchDocs["query"]["bool"]["filter"][0]["range"]["post_date"]["lte"]= str(startYear+((i+1) *offset))+"-01||/M"
#        searchDocs["query"]["bool"]["must"][0]["match"]["post_body"] = keyword
#
#        res = es.search(index="nkdb", body=searchDocs)
#        numOfDocs = res["hits"]["total"]["value"]
#        searchDataArr.append(numOfDocs)
#
#        print(numOfDocs)
#
#    dic = {}
#    resultWholeArr = []
#    resultSearchArr = []
#    # Angular Data Format{ y: 150, label: "Dec" }
#    for i in range(0, 8):
#        dic["y"] = wholeDataArr[i]
#        dic["label"] = str(startYear+(i*offset))
#
#        resultWholeArr.append(dic)
#        dic = {}
#        dic["y"] = searchDataArr[i]
#        dic["label"] = str(startYear+(i*offset))
#        resultSearchArr.append(dic)
#
#        dic = {}
#
#    resultArr.append(resultWholeArr)
#    resultArr.append(resultSearchArr)
#
#    print(resultArr)
#
#    return json.dumps(resultArr, ensure_ascii=False)
#
#
#@app.route('/test', methods=['POST', 'GET'])
#def test():
#    if request.method == 'POST':
#        result = request.json
#        keyword = result["keyword"]
#
#    body = {
#        "query": {
#            "match_all": {}
#        },
#        "size": 1000,
#    }
#
#    res = es.search(index="nkdb", body=body)
#
#    resultArr = res["hits"]["hits"]
#
#    dateArr = []
#
#    dayCntDic = {}
#
#    for i in resultArr:
#        dateArr.append(i["_source"]["post_date"])
#
#    for i in dateArr:
#        day = i[8:10]
#
#        if day in dayCntDic:
#            dayCntDic[day] += 1
#        else:
#            dayCntDic[day] = 1
#
#    resultDic = []
#    dic = {}
#
#    for day, cnt in sorted(dayCntDic.items()):
#        dic["y"] = cnt
#        dic["label"] = day
#        resultDic.append(dic)
#        dic = {}
#
#    return json.dumps(resultDic, ensure_ascii=False)
#
#
## def rank(contents):
##      #split the text by sentences
##     sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', contents)
#
#
##     #normalize the text
##     contents = [normalize(text, number=True) for text in sentences]
#
##     wordrank_extractor = KRWordRank(
##         min_count = 7,  # Minimum frequency of word
##         max_length=10,  # Maximum length of word
##         verbose = True
##     )
#
##     beta = 0.85  # Decaying factor beta of PageRank
##     max_iter = 10
#
##     keywords, rank, graph = wordrank_extractor.extract(contents, beta, max_iter)
#
##     result=[]
##     dic={}
##     #Make a dictionary [word, weight]
##     for word, r in sorted(keywords.items(), key=lambda x:x[1], reverse=True)[:30]:
##         dic["y"]=r
##         dic["label"]=word
##         result.append(dic)
##         dic={}
#
##     return result
#
#@app.after_request
#def after_request(response):
#
#    # response.headers.add('Access-Control-Allow-Origin', '*')
#    # response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
#    return response
#

#서버 구동
app.run(host="0.0.0.0",port=5000, debug=True)

