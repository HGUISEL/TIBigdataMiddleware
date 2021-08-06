#-*- coding:utf-8 -*-
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> origin/master
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

<<<<<<< HEAD
from flask import Flask, jsonify, request, Response, render_template
=======
from flask import Flask, jsonify, request, Response
>>>>>>> upstream/master
=======
from flask import Flask, jsonify, request, Response
>>>>>>> origin/master
from flask_restful import Resource, Api
from elasticsearch import Elasticsearch
from flask_cors import CORS, cross_origin
from collections import Counter
from operator import itemgetter
import time
import json
import sys
<<<<<<< HEAD
<<<<<<< HEAD
#from rcmdHelper import rcmd as rc

from common.cmm import INDEX
=======
from rcmdHelper import rcmd as rc
>>>>>>> upstream/master
=======
#from rcmdHelper import rcmd as rc

from common.cmm import INDEX
>>>>>>> origin/master

import os
if os.name == "nt":
    from eunjeon import Mecab
else:
    from konlpy.tag import Mecab
print("os system : ", os.name)

sys.path.insert(0, './common')

# Sentence-tokenizer
import re
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> origin/master
#import tfidf
import tfidf_all
# Implement KR-Wordrank
# from krwordrank.hangle import normalize
# from krwordrank.word import KRWordRank
import datetime
import time
<<<<<<< HEAD
=======
import tfidf
# Implement KR-Wordrank
from krwordrank.hangle import normalize
from krwordrank.word import KRWordRank
>>>>>>> upstream/master
=======
>>>>>>> origin/master

app = Flask(__name__)
# app.config['TESTING'] = True
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> origin/master
isLocalEs = 0
#local es mode:
if(isLocalEs):
    # Url address of Elasticsearch
    import socket
    def get_ip_address():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

    serverUrl = get_ip_address()  # '192.168.0.110'
    print(serverUrl)
    if(serverUrl != "http://203.252.112.15:9200"):
        serverUrl="http://localhost:9200"
    else:
        serverUrl = "http://elastic:epp2020@203.252.112.14"
else:
    serverUrl = "http://elastic:epp2020@203.252.112.14"
<<<<<<< HEAD
=======

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
    serverUrl = "http//203.252.112.14:9200"
>>>>>>> upstream/master

=======
>>>>>>> origin/master
# ElasticSearch connection
es = Elasticsearch(serverUrl)
app = Flask(__name__)
api = Api(app)

<<<<<<< HEAD
<<<<<<< HEAD
# CORS(app, support_credentials=True)
#CORS(app)
#cors =CORS(app, resource ={r" ":{"":""}})
#app.config['CORS_HEADERS'] = 'Content-Type'

#################################################
from TextMining.Tokenizer.kubic_mystorage import *
from TextMining.Tokenizer.kubic_data import *
from TextMining.Tokenizer.kubic_morph import *
from TextMining.Analyzer.kubic_wordCount import *
from TextMining.Analyzer.kubic_tfidf import *
import kubic_sslFile as kubic_ssl
from bson import json_util
import subprocess
import schedule
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError

#angular 사전메세지를 위한 코드
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

#TextMining
@app.route("/preprocessing",methods=['GET', 'POST']) #서버 켜져있는 방법알기위해서 GET 사용
def preprocessing():
    app=Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR']=True
    print("************************Preprocessing************************")

### Angular + Flask    
    # 전처리 실행 버튼 -> 메세지를 유저한테 back -> user ip에서 post를 preprocessing으로 보내 -> 
    # 플라스크 request response를 받는 method를 써서 json을 까서 사용
    # Angular에서 보내는 data 
    if request.method == 'POST':
        data = request.json
        print(data, type(data))
        email = data['userEmail']
        keyword = data['keyword']
        savedDate = data['savedDate']
        wordclass = data['wordclass']

        stopwordTF = data['stopword']
        synonymTF = data['synonym']
        compoundTF = data['compound']

    # email = 'sujinyang@handong.edu'                                                                        
    # keyword = '북한'
    # savedDate = '2021-07-08T11:46:03.973Z'
    # wordclass = '010'

    if(checkEmail(email) == False): #외부 해킹을 대비해 email을 mongodb에 있는 사용자인지 확인하기
        return json.dump({'returnCode': 401, 'errMsg': '로그인정보가 없습니다'}) #returnCode, errMsg

### compound가 true라면 사용자사전 적용, false면 기본 default 사용자사전으로 적용하기
    # result = compound(email, keyword, savedDate, wordclass, stopwordTF, synonymTF, compoundTF)
    result = compound(email, keyword, savedDate, wordclass)
    
    #print("전처리 결과\n", result[0], result[1])

    if result[0] == False: #사용자사전 format안맞을 때
        resultDic = {'returnCode':'400', 'errMsg':result[1], #'returnDate' : datetime.datetime.now(), 
'activity' : 'preprocessing', 'email' : email, 'keyword' : keyword, 'savedDate' : savedDate}
        return json.dumps(resultDic, ensure_ascii=False, default=json_util.default)
       
    else:
        resultDic = {#'returnDate' : datetime.datetime.now(), 
'activity' : 'preprocessing', 'email' : email, 'keyword' : keyword, 'result' : result[1][:100], 'savedDate' : savedDate}
        return json.dumps(resultDic, ensure_ascii=False, default=json_util.default) 

schedPP = BackgroundScheduler(daemon=True)
schedPP.add_job(preprocessing)
schedPP.start()

#@app.route("/textmining",methods=['GET', 'POST'])
def textmining():
    app=Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR']=True
    print("************************Textmining************************")

    ### Angular post data
    if request.method == 'POST':
        data = request.json
        print(data, type(data))
        email = data['userEmail']
        keyword = data['keyword']
        savedDate = data['savedDate']
        #optionList = data['optionList']
        #analysisName = data['analysisName']

    #test1
    email = 'sujinyang@handong.edu'                                                                        
    keyword = '북한'
    savedDate = '2021-07-08T11:46:03.973Z'
    wordclass = '010'

    # #test2
    # email = '21600280@handong.edu'
    # keyword = '통일'
    # savedDate = "2021-07-13T17:21:40.973Z"
    # wordclass = '010'

    optionList = 100
    analysisName = 'count'

    if analysisName == 'count':
        print("빈도수 분석을 시작합니다\n")
        result = word_count(email, keyword, savedDate, optionList)
        print("\n빈도수 분석 결과\n", result)
        resultDic = {#'returnDate' : datetime.datetime.now(), 
        'activity' : 'count', 'email' : email, 
        'keyword' : keyword, 'savedDate' : savedDate, 'optionList' : optionList, 'result' : result}
    
    elif analysisName == 'tfidf':
        print("tfidf 분석을 시작합니다\n")
        result = tfidf(email, keyword, savedDate, optionList)
        print("\ntfidf 분석 결과\n", result)
        resultDic = {#'returnDate' : datetime.datetime.now(), 
        'activity' : 'count', 'email' : email, 
        'keyword' : keyword, 'savedDate' : savedDate, 'optionList' : optionList, 'result' : result}

    return json.dumps(resultDic, default=json_util.default, ensure_ascii=False)

# schedTM = BackgroundScheduler(daemon=True)
# schedTM.add_job(textmining)
# schedTM.start()

###################################################################################################################
'''
#################################################
=======

# CORS(app, support_credentials=True)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

#################################################
>>>>>>> origin/master
#"""
#SVM
#2020.09.
#"""
#################################################
import SVM
import schedule
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError


#@app.route('/svm', methods=['GET'])#app객체로 라우팅 경로 설정
def svm():
    app=Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR']=True

    now=datetime.datetime.now()
    date=now.strftime('%Y-%m-%d')

    filename='./log/svm.log'
    with open(filename, "a") as f:
        f.write(date)
        f.write("\n")
    print("svm.log에 모델예측 실행 날짜를 기록하였습니다.")
    result=SVM.MoEs(date)
    return json.dumps(result, ensure_ascii=False)
#@app.route('/train', methods=['GET'])#app객체로 라우팅 경로 설정
def svm_train():
    pp = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    now=datetime.datetime.now()
    date=now.strftime('%Y-%m-%d')

    filename='./log/svm_train.log'
    with open(filename, "a") as f:	
        f.write(date)
        f.write("\n")
    print("svm_train.log에 모델학습 실행 날짜를 기록하였습니다.")
    result=SVM.SVMTrain()
    print("SVM 모델 학습을 완료하였습니다.")
    return "SVM 모델 학습 완료"

#sched_train = BackgroundScheduler(daemon=True)
#sched_train.add_job(svm_train,'interval',hours=24)
#sched_train.add_job(svm_train)
#sched_train.start()

<<<<<<< HEAD
sched = BackgroundScheduler(daemon=True)
sched.add_job(svm)
sched.start()
=======
#sched = BackgroundScheduler(daemon=True)
#sched.add_job(svm)
#sched.start()
>>>>>>> origin/master

#################################################
#"""
#CNN
#2021.02.
#"""
#################################################
import CNN
import schedule
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError

#@app.route('/svm', methods=['GET'])#app객체로 라우팅 경로 설정
def cnn():
    pp = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d')


    filename = './log/cnn.log'
    with open(filename,"a") as f:
        f.write(date)
        f.write("\n")
    print("날짜를 기록하였습니다")
    result=CNN.MoEs(date)
    return json.dumps(result, ensure_ascii=False)

#@app.route('/train', methods=['GET'])#app객체로 라우팅 경로 설정
def cnn_train():
    pp = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    now=datetime.datetime.now()
    date=now.strftime('%Y-%m-%d')

    filename='./log/cnn_train.log'
    with open(filename, "a") as f:
        f.write(date)
        f.write("\n")
    print("cnn_train.log에 모델학습 실행 날짜를 기록하였습니다.")
    result=CNN. cnn_train()
    print("CNN 모델 학습을 완료하였습니다.")
    return "CNN 모델 학습 완료"   

#sched_train = BackgroundScheduler(daemon=True)
#sched_train.add_job(cnn_train,'interval',hours=24)
#sched_train.add_job(cnn_train)
#sched_train.start()

<<<<<<< HEAD
#sched = BackgroundScheduler(daemon=True)
#sched.add_job(cnn)
#sched.start()
=======
sched = BackgroundScheduler(daemon=True)
sched.add_job(cnn)
sched.start()
>>>>>>> origin/master

#################################################
#"""
#Multi-SVM
#2021.02
#"""
#################################################
import Multi_SVM
import schedule
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError

#@app.route('/svm', methods=['GET'])#app객체로 라우팅 경로 설정
def multi_SVM():
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d')

    filename = './log/multi_svm.log'
    with open(filename,"a") as f:
        f.write(date)
        f.write("\n")
    print("날짜를 기록하였습니다")
    result=multi_SVM.MoEs(date)
    return json.dumps(multi_SVM, ensure_ascii=False)

#@app.route('/train', methods=['GET'])#app객체로 라우팅 경로 설정
def multi_SVM_train():
    pp = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    now=datetime.datetime.now()
    date=now.strftime('%Y-%m-%d')

    filename='./log/multi_svm_train.log'
    with open(filename, "a") as f:
        f.write(date)
        f.write("\n")
    print("multi_svm_train.log에 모델학습 실행 날짜를 기록하였습니다.")
    result=Multi_SVM.SVMTrain()
    print("MULTI_SVM 모델 학습을 완료하였습니다.")
    return "MULTI_SVM 모델 학습 완료"

#sched_train = BackgroundScheduler(daemon=True)
#sched_train.add_job(multi_SVM_train)
#sched_train.add_job(multi_SVM_train,'interval',hours=24)
#sched_train.start()

#sched = BackgroundScheduler(daemon=True)
#sched.add_job(multi_SVM)
#sched.start()

################################################################

#@app.route("/tfidfRaw",methods=['GET'])


"""
<<<<<<< HEAD
=======

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



@app.route("/tfidfRaw",methods=['GET'])
>>>>>>> upstream/master
=======
>>>>>>> origin/master
def tfidfRaw():
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    Numdoc = 600

    contents = tfidf.getTfidfRaw(Numdoc)
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> origin/master
    return json.dumps(contents, ensure_ascii=False)
"""
#@app.route("/allTfidfTable",methods=['GET'])

def allTfidfTable():
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    print("get request")
    tfidf_all.getAllTfidfTable()

    sys.exit()
<<<<<<< HEAD

'''
###################################################################################################################

=======
>>>>>>> origin/master
#sched_train = BackgroundScheduler(daemon=True)
#sched_train.add_job(allTfidfTable)
#sched_train.add_job(multi_SVM_train,'interval',hours=24)
#sched_train.start()
#@app.route("/tfidfTable",methods=['GET'])
"""
<<<<<<< HEAD
=======
    #return json.dumps(contents, ensure_ascii=False)
    return json.dumps(contents, ensure_ascii=False)

@app.route("/tfidfTable",methods=['GET'])
>>>>>>> upstream/master
=======
>>>>>>> origin/master
def tfidfTable():
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

<<<<<<< HEAD
<<<<<<< HEAD
    Numdoc = 3
=======
    Numdoc = 600
>>>>>>> upstream/master
=======
    Numdoc = 3
>>>>>>> origin/master

    contents = tfidf.getTfidfTable(Numdoc)
    #return json.dumps(contents, ensure_ascii=False)
    return json.dumps(contents, ensure_ascii=False)
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> origin/master
"""
#########################################
# 191227 ES Test update : use esFunc module
"""
<<<<<<< HEAD
=======

#########################################
# 191227 ES Test update : use esFunc module
>>>>>>> upstream/master
=======
>>>>>>> origin/master
from common import esFunc
@app.route('/esTest', methods=['GET'])
def esTest():
    result = esFunc.esGetDocs(9)
    
    return json.dumps(result, ensure_ascii=False)

<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> origin/master
@app.route('/testRead', methods=['GET'])
def testRead():
    result = esFunc.dataLoad()

    return json.dumps(result, ensure_ascii=False)
"""
<<<<<<< HEAD
=======


>>>>>>> upstream/master
=======
>>>>>>> origin/master
################################################
"""
LDA 잠재 디리클레 할당 모듈화
2019.12.27.
"""
################################################
# With LDA gensim library
<<<<<<< HEAD
<<<<<<< HEAD
# import LDA
"""
=======
import LDA
>>>>>>> upstream/master
=======
# import LDA
"""
>>>>>>> origin/master
@app.route('/lda', methods=['GET'])
def lda():
    app = Flask(__name__)
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    result = LDA.LDA(10) ##문서 10개 돌림 
    # print
    return json.dumps(result, ensure_ascii=False)
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> origin/master
"""
#recomandation function
#@app.route('/rcmd', methods=['GET', 'POST'])
#def rcmd():
#    print("recomandation function init.")

#    if request.method == 'POST':
#        req = request.json
#        idList = req["idList"]

#     # print("Get id list from Front-End: ",idList)

#    rcmdList = rc.getRcmd(idList)
#    print("rcmd function done!")
#    
#    return json.dumps(rcmdList, ensure_ascii=False)


"""
<<<<<<< HEAD
=======

#recomandation function
@app.route('/rcmd', methods=['GET', 'POST'])
def rcmd():
    print("recomandation function init.")

    if request.method == 'POST':
        req = request.json
        idList = req["idList"]

    # print("Get id list from Front-End: ",idList)

    rcmdList = rc.getRcmd(idList)
    print("rcmd function done!")
    
    return json.dumps(rcmdList, ensure_ascii=False)



>>>>>>> upstream/master
=======
>>>>>>> origin/master
def textRank():
    import json
    from gensim.summarization import keywords
    DIR_FE = "../Front_KUBIC/src/assets/special_first/ctgRNNResult.json"

    with open(DIF_FE,'r',encoding='utf-8') as fp:
        data = json.load(fp)

    corpus = data[0]["doc"]


    isTokened = True

    if isTokened == True:
        tokenized_doc = []
        for doc in corpus:
            tokenized_doc.append(doc["words"])
    else:
        contents = []
        for doc in corpus:
            contents.append(doc["contents"])

        tagger = Mecab()
        print("데이터 전처리 중... It may takes few hours...")
        tokenized_doc = [tagger.nouns(contents[cnt]) for cnt in range(len(contents))]

<<<<<<< HEAD
<<<<<<< HEAD
=======
    # texts = """
    # □ 평화번영을 위한 남북관계 발전방안「6.15공동선언」 이후 남북관계는 빠른 속도로 발전하고 있습니다. 그러나 장기간에 걸친 분단으로 인해 냉전적 사고와 논리, 불신이 남과 북의 관계 진전에 발목을 잡고 있는 것도 사실입니다.공존공영의 남북관계를 정립하기 위해서는 무엇보다 상호신뢰를 쌓기 위한 노력과, 이를 뒷받침할 수 있는 통일교육 지원 등의 국내적 기반 조성도 필요합니다.우리 민주평화통일자문회의 위원들은 한반도의 평화번영을 위한 남북관계의 발전을 위해 다음의 건의를 드립니다.첫 째, 남과 북이 서로 만날 수 있는 기회를 많이 만들어내야 합니다.대구 유니버시아드대회를 통해 우리는 북한 주민들이 우리와 얼마나 다른 사고와 행동을 하는지 생생히 보았습니다.남과 북이 서로를 이해하고 화합하기 위해서는 무엇보다 먼저 많이 만나는 것이 필요합니다.둘 째, 지방자치단체와 시민사회단체 등의 남북교류가 활성화되어야 합니다.남북한 관계가 탄탄한 뿌리를 내리기 위해서는 남과 북을 잇는 다양한 네트워크가 필요합니다. 먼저 지방자치단체간 자매결연을 통한 협력체제를 구축하고, 시민사회단체간에도 연대를 맺는 활동이 필요합니다.이들 상호간의 남북교류는 안정적인 남북관계를 뒷받침하는 든든한 버팀목이 될 수 있을 것입니다.셋 째, 인도주의적 대북지원이 적극적으로 확대되어야 합니다.인도주의 정신에 입각한 대북지원은 정치적 논리를 초월하여 실천해야 할 매우 중요한 과제입니다. 일회성 지원이나 이벤트성 행사보다는 지속적인 지원이 절실히 필요합니다.범국민적 차원에서 폭넓게 펼칠 수 있는 북한에 나무심기 운동, 북한 어린이 돕기운동 등이 좋은 예가 될 수 있을 것입니다.넷 째, 제2차 남북정상회담이 빠른 시일 내에 열리기를 기대합니다.북핵문제 해결 등 한반도의 평화체제 구축을 위한 역사적 전기 마련이 필요한 시점입니다.제2차 정상회담을 통해 보다 밝은 남북관계를 재정립하고, 동북아의 안정에도 기여할 수 있을 것입니다.□ 국민통합과 한민족 통일역량 결집방안한반도에서의 평화와 번영의 성취는 동북아뿐만 아니라 전세계의 평화와 번영에도 긴요하다는 점에서 하루빨리 이루어야 할 민족적 과제입니다. 따라서 7천만 국내외 동포의 통일역량의 결집은 장차 한반도 통일에 결정적 담보가 될 것 입니다.해외동포는 통일을 위한 가교의 역할로, 남북한 주민은 서로를 이해하는 넓은 아량으로 그리고 우리 사회 내부는 겨레가 함께 살아갈 수 있는 의지를 모아 새로운 시대에 새로운 한민족 공동체를 창조하는 데 적극적으로 참여하여야 합니다.우리 민주평화통일자문회의 위원들은 국민대통합과 한민족의 통일역량 결집을 위해 다음의 건의를 드립니다.첫 째, 분단의 결과로 생긴 민족내부의 차이와 갈등을 폭넓게 수용하는 정책이 필요합니다.냉전적 사고에 사로잡힌 불신과 대결로는 민족의 통일역량을 결집할 수 없습니다. 다양한 의견과 차이를 인정하고 이를 공존의 기초로 받아들이는 포용의 자세가 필요합니다.국내는 물론 현지사회에 동화된 한민족의 일원도 차이와 갈등을 넓게 아우르는 민족대통합의 정책이 필요합니다.둘 째, 한민족 경제·문화 공동체를 만들어 민족상생의 시대를 열어야 합니다.세계화 시대에 각 나라에 거주하는 해외동포들이 경제·사회적으로 주류에 서서 한민족의 정체성을 유지할 수 있도록, 그리고 현지 국민들과 융화하면서 자긍심을 유지·발전시킬 수 있도록 지원해야 합니다.한민족 경제·문화공동체를 형성하기 위해 현지 한국어 교육의 강화, 청년세대의 상호 교류, 지역사회내의 다양한 네트워크 형성으로 한민족의 정체성을 강화하여야 합니다.또한 현지 국민들과의 융화를 위해 이미 설립되어 있거나 설립해야 할 「한국 문화센터」에 지원을 아끼지 말아야 합니다.셋 째, 민주평통 해외자문위원의 역할을 강화할 필요가 있습니다.동북아 중심국가로 성장하는 통일한국의 건설에는 국민대통합과 함께 해외동포의 역량결집이 대단히 중요합니다. 특히 한민족의 10% 이상인 7백만이 해외에 살고 있다는 점은 큰 자산이라 할 수 있습니다.해외동포의 통일역량을 효과적으로 결집하는 데 민주평통 해외위원의 참여와 역할이 대단히 중요한 비중을 차지하고 있습니다. 이를 위한 제도적 장치가 시급히 마련되어야 합니다.
    # """

>>>>>>> upstream/master
=======
>>>>>>> origin/master
    # with open("krWl.txt", "r" ,encoding='utf-8') as f:
    #     texts = f.read() 
        # print(f.read())
        # tokenized_doc = tagger.nouns(texts)
        # tokenized_doc = ' '.join(tokenized_doc) 
        # print("형태소 분석 이후 단어 토큰의 개수",len(tokenized_doc)) 

<<<<<<< HEAD
<<<<<<< HEAD
    # result = keywords(tokenized_doc, words = 15 , scores=True)
    result = keywords(tokenized_doc)

=======
    result = keywords(tokenized_doc, words = 15 , scores=True)
>>>>>>> upstream/master
=======
    # result = keywords(tokenized_doc, words = 15 , scores=True)
    result = keywords(tokenized_doc)

>>>>>>> origin/master
    # with open(DIR_FE, 'w', -1, "utf-8") as f:
    with open("./wrCul.json", 'w', -1, "utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    return json.dumps(result, ensure_ascii=False)
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> origin/master
"""
"""
def wordRank():
    #Retreive text from elasticsearch
    results = es.get(index=INDEX, doc_type='nkdb', id='5dc9fc5033ec463330e97e94')
<<<<<<< HEAD
=======

def wordRank():
    #Retreive text from elasticsearch
    results = es.get(index='nkdb', doc_type='nkdb', id='5dc9fc5033ec463330e97e94')
>>>>>>> upstream/master
=======
>>>>>>> origin/master
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
<<<<<<< HEAD
<<<<<<< HEAD
"""
"""
=======

>>>>>>> upstream/master
=======
"""
"""
>>>>>>> origin/master
@app.route('/wordrank', methods=['GET'])
def chseAlg():
    try: 
        result = wordRank()
    except:
        result =  textRank()
    return result
<<<<<<< HEAD
<<<<<<< HEAD
"""
"""
=======
    
>>>>>>> upstream/master
=======
"""
"""
>>>>>>> origin/master
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
    for i in range(0, 8):

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
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> origin/master
        # print("query body has been built!")
        res = es.search(index=INDEX, body=allDocs)
        # print(res)

<<<<<<< HEAD
=======

        res = es.search(index="nkdb", body=allDocs)
>>>>>>> upstream/master
=======
>>>>>>> origin/master
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
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> origin/master
        # print("ready to search")
        res = es.search(index=INDEX, body=searchDocs)
        print(res)
        numOfDocs = res["hits"]["total"]["value"]
        searchDataArr.append(numOfDocs)

        # print(numOfDocs)
<<<<<<< HEAD
=======

        res = es.search(index="nkdb", body=searchDocs)
        numOfDocs = res["hits"]["total"]["value"]
        searchDataArr.append(numOfDocs)

        print(numOfDocs)
>>>>>>> upstream/master
=======
>>>>>>> origin/master

    dic = {}
    resultWholeArr = []
    resultSearchArr = []
    # Angular Data Format{ y: 150, label: "Dec" }
    for i in range(0, 8):
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

<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> origin/master
    # print(resultArr)

    return json.dumps(resultArr, ensure_ascii=False)

"""
"""
<<<<<<< HEAD
=======
    print(resultArr)

    return json.dumps(resultArr, ensure_ascii=False)


>>>>>>> upstream/master
=======
>>>>>>> origin/master
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

<<<<<<< HEAD
<<<<<<< HEAD
    res = es.search(index=INDEX, body=body)
=======
    res = es.search(index="nkdb", body=body)
>>>>>>> upstream/master
=======
    res = es.search(index=INDEX, body=body)
>>>>>>> origin/master

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
<<<<<<< HEAD
<<<<<<< HEAD
"""
=======

>>>>>>> upstream/master
=======
"""
>>>>>>> origin/master

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
<<<<<<< HEAD
<<<<<<< HEAD
#         dic["label"]=wordkeyword
=======
#         dic["label"]=word
>>>>>>> upstream/master
=======
#         dic["label"]=wordkeyword
>>>>>>> origin/master
#         result.append(dic)
#         dic={}

#     return result
<<<<<<< HEAD

<<<<<<< HEAD
"""
@app.after_request
def after_request(response):
=======
"""
@app.after_request
def after_request(response):

>>>>>>> origin/master
   # response.headers.add('Access-Control-Allow-Origin', '*')
   # response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response
<<<<<<< HEAD
"""    

if __name__ == "__main__":
    # flask run(실행하면 port를 정해줄수 있는데 default는 5000): 5000 , python app.py는 5050
    # 앞으로 Angular에서 5050으로 보내줄 것임
#    app.run(host="0.0.0.0", port=5050) 
    context=(kubic_ssl.crt,kubic_ssl.key) #gitignore 비밀경로
    app.run(host='0.0.0.0', port=15000, ssl_context=context)     
=======
@app.after_request
def after_request(response):

    # response.headers.add('Access-Control-Allow-Origin', '*')
    # response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


app.run(host="0.0.0.0",port=5000, debug=True)
>>>>>>> upstream/master
=======
"""
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
>>>>>>> origin/master
