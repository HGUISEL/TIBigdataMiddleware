#-*- coding:utf-8 -*-
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from flask import Flask, jsonify, request, Response, render_template, copy_current_request_context, current_app, abort
from flask_restful import Resource, Api
from elasticsearch import Elasticsearch
from flask_cors import CORS, cross_origin
from collections import Counter
from operator import itemgetter
import time
import json
import sys
from rcmdHelper import rcmd as rc


#error
#from common.cmm import INDEX

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

#import wordCount For all datas
import wordCount_all
import datetime
import time

app = Flask(__name__)
# app.config['TESTING'] = True
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

isLocalEs = 0
#local es mode:
# Url address of Elasticsearch

#esAccount.address(isLocalEs)
import topic_analysis.esAccount as esAcc
# ElasticSearch connection

es = Elasticsearch(
        [esAcc.host],
        http_auth=(esAcc.id, esAcc.password),
        scheme="https",
        port= esAcc.port
    )

# app = Flask(__name__) 
api = Api(app)

CORS(app, support_credentials=True)
#CORS(app)
#cors =CORS(app, resource ={r" ":{"":""}})
#app.config['CORS_HEADERS'] = 'Content-Type'


##############loging####################
import logging
import traceback

log_filename = "kubic_flask_" + str(datetime.datetime.now()) + ".log"
logging.basicConfig(filename = "log_flask/"+log_filename, level=logging.INFO, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
app.logger.info("log start")

#########################################


from TextMining.Tokenizer.kubic_mystorage import *
from TextMining.Tokenizer.kubic_data import *
from TextMining.Tokenizer.kubic_morph import *
from TextMining.Analyzer.kubic_wordCount import *
from TextMining.Analyzer.kubic_tfidf import *
from TextMining.Analyzer.kubic_semanticNetworkAnalysis import *
from TextMining.Analyzer.kubic_kmeans import *
from TextMining.Analyzer.kubic_ngrams import *
from TextMining.Analyzer.kubic_hcluster import *
from TextMining.Analyzer.kubic_topicLDA import *
from TextMining.Analyzer.kubic_word2vec import *

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

#TextMining package 실행
@app.route("/preprocessing",methods=['GET', 'POST']) #서버 켜져있는 방법알기위해서 GET 사용
def preprocessing():
    #21.08.11 app=Flask(__name__)
    #21.08.11 app.config['JSONIFY_PRETTYPRINT_REGULAR']=True

### Angular + Flask    
    # 전처리 실행 버튼 -> 메세지를 유저한테 back -> user ip에서 post를 /preprocessing으로 보냄 -> 
    # 플라스크 request method로 Angular가 보내는 json data 받아서 사용

    try:
        # Angular에서 보내는 data 
        if request.method == 'POST':
            data = request.json
            
            identification = str(data['userEmail'])+'_'+'preprocessing'+'_'+str(data['savedDate'])+"// "
            
            app.logger.info(identification+"전처리를 시작합니다")
            app.logger.info(identification+"request data를 받아왔습니다.")
            
            email = data['userEmail']
            keyword = data['keyword']
            savedDate = data['savedDate']
            wordclass = data['wordclass']

            stopwordTF = data['stopword']
            synonymTF = data['synonym']
            compoundTF = data['compound']
        else: return 'GET result' # 지영수정

    except KeyError as e:
        err = traceback.format_exc()
        app.logger.error(identification+"request 키 에러입니다. request에 다음과 같은 키가 존재하지 않습니다. \n:"+str(err))
        resultDic = {'returnCode': 400, 'errMsg': "request 키 에러입니다. request에 다음과 같은 키가 존재하지 않습니다. \n:"+str(e)}
        return json.dumps(resultDic, ensure_ascii=False, default=json_util.default)


    if(checkEmail(email) == False): #외부 해킹을 대비해 email을 mongodb에 있는 사용자인지 확인하기
        # return json.dump({'returnCode': 401, 'errMsg': '로그인정보가 없습니다'}) #returnCode, errMsg
        app.logger.error(identification+ "로그인 정보가 없습니다.")
        return jsonify({'returnCode': 400, 'errMsg': '로그인 정보가 없습니다'})

    # result = compound(email, keyword, savedDate, wordclass)
    # result = compound(email, keyword, savedDate, wordclass, stopwordTF, synonymTF, compoundTF)
    result_add_title = compound_add_text(email, keyword, savedDate, wordclass, stopwordTF, synonymTF, compoundTF)
    if result_add_title[0] == False:
        app.logger.error(identification+ "전처리에 실패하였습니다. \n 실패사유:" + result_add_title[1])
        return jsonify({'returnCode': 400, 'errMsg': "전처리에 실패하였습니다. \n 실패사유:" + result_add_title[1]})
    #print("전처리 결과\n", result[0], result[1])

    # if result_add_title[0] == False: #사용자사전 format안맞을 때
    #     resultDic = {'returnCode': 400, 'errMsg': ""result_add_title[1]}
    #     app.logger.info(identification+ "전처리가 완료되었습니다")
    #     return json.dumps(resultDic, ensure_ascii=False, default=json_util.default)
    else:
        resultDic = {'returnCode': 200, 
        'activity' : 'preprocessing', 'email' : email, 'keyword' : keyword, 'result' : result_add_title[1], 'savedDate' : savedDate}
        app.logger.info(identification+ "전처리가 완료되었습니다")
        return json.dumps(resultDic, ensure_ascii=False, default=json_util.default)



@app.route("/textmining",methods=['GET', 'POST'])
def textmining():
    
#     return textmining_request(request)
    
# # @copy_current_request_context 
# def textmining_request(req):

    #21.08.11 app=Flask(__name__)
    #21.08.11 app.config['JSONIFY_PRETTYPRINT_REGULAR']=True
    # print("************************Textmining************************")
    ### Angular post data

    try: 
        # current_app.preprocess_request()
        print("got request")
        if request.method == 'POST':
            data = request.json 
            identification = str(data['userEmail'])+'_'+'textmining'+'_'+str(data['savedDate'])+"// "
            email = data['userEmail']
            keyword = data['keyword']
            savedDate = data['savedDate']
            optionList = data['option1']
            analysisName = data['analysisName']
        else: return 'GET result'
    except Exception as e :
        err = traceback.format_exc()
        identification = str(data['userEmail'])+'_'+'textmining'+'_'+str(data['savedDate'])+"// "
        app.logger.error(identification+"request 키 에러입니다. request에 다음과 같은 키가 존재하지 않습니다. \n:"+str(err))
        resultDic = {'returnCode': 400, 'errMsg': "request 키 에러입니다. request에 다음과 같은 키가 존재하지 않습니다. \n:"+str(e)}
        return json.dumps(resultDic, default=json_util.default, ensure_ascii=False)


    # email = '21600280@handong.edu'
    # keyword = "통일"
    # savedDate = "2021-08-06T11:52:05.706Z"


    if analysisName == 'count':
        app.logger.info(identification + "빈도수 분석 시작")
        result_table, result_graph, analysisInfo = word_count(email, keyword, savedDate, optionList, analysisName)
        if result_table == 'failed':
            app.logger.error(identification + "빈도수 분석 실패")
            resultDic = {'returnCode': 400, 'errMsg': "빈도수 분석 실패 \n"+ result_graph}
        else:
            app.logger.error(identification + "빈도수 분석 성공")
            resultDic = {'returnCode': 200, #'returnDate' : datetime.datetime.now(), 
            'activity' : analysisName, 'email' : email, 
            'keyword' : keyword, 'savedDate' : savedDate, 'analysisDate': analysisInfo["analysis_date"], 'optionList' : optionList, 
            'result_table' : result_table, 'result_graph': result_graph,
            "jsonDocId": analysisInfo["doc_id"]}

    
    elif analysisName == 'tfidf':
        app.logger.info(identification + "tfidf 분석 시작")
        result_table, result_graph, analysisInfo = tfidf(email, keyword, savedDate, optionList, analysisName)
        if result_table == 'failed':
            app.logger.error(identification + "tfidf 분석 실패")
            resultDic = {'returnCode': 400, 'errMsg': "tfidf 분석 실패 \n"+ result_graph}
        else:
            resultDic = {'returnCode': 200, #'returnDate' : datetime.datetime.now(), 
            'activity' : analysisName, 'email' : email, 
            'keyword' : keyword, 'savedDate' : savedDate, 'analysisDate': analysisInfo["analysis_date"], 'optionList' : optionList, 
            'result_table' : result_table, 'result_graph': result_graph, 
            "jsonDocId": analysisInfo["doc_id"]}

    # for semanticNetworkAnalysis
    elif analysisName == 'network':
        try:
            linkStrength = data['option2']
            if linkStrength == None:
                raise Exception("option2가 비어있습니다!")
        except Exception as e:
            err = traceback.format_exc()
            app.logger.error(identification+"request 키 에러입니다. request에 다음과 같은 키가 존재하지 않습니다. \n:"+str(err))
            resultDic = {'returnCode': 400, 'errMsg': "request 키 에러입니다. request에 다음과 같은 키가 존재하지 않습니다. \n:"+str(e)}

        app.logger.info(identification + "의미연결망 분석 시작" )
        result_graph, result_table, analysisInfo = semanticNetworkAnalysis(email, keyword, savedDate, optionList, analysisName, linkStrength)

        if result_graph == "failed":
            app.logger.error(identification + "의미연결망 분석 실패")
            resultDic = {'returnCode': 400, 'errMsg': "의미연결망 분석 실패 \n"+ result_table}
        else:
            resultDic = {'returnCode': 200,  #'returnDate' : datetime.datetime.now(), 
            'activity' : analysisName, 'email' : email,
            'keyword' : keyword, 'savedDate' : savedDate, 'analysisDate': analysisInfo["analysis_date"], 
            'option1' : optionList, "option2" : linkStrength, 
            'result_table' : result_table, 'result_graph': result_graph, 
            "jsonDocId": analysisInfo["doc_id"]}
    
    # for kmeans
    elif analysisName == 'kmeans':
        app.logger.info(identification + "kmeans 분석 시작")
        result1, result2, analysisInfo = kmeans(email, keyword, savedDate, optionList, analysisName)
        if result1 == True:        
            resultDic = {'returnCode': 200,#'returnDate' : datetime.datetime.now(), 
            'activity' : analysisName, 'email' : email,
            'keyword' : keyword, 'savedDate' : savedDate,'analysisDate': analysisInfo["analysis_date"], 'optionList' : optionList, 
            'result_graph' : result2,
            "jsonDocId": analysisInfo["doc_id"]}
        else:
            app.logger.error(identification + "kmeans 분석 실패")
            resultDic = {'returnCode': 400, 'errMsg': "분할군집분석 실패 \n"+ result2}
        
    # for ngrams
    elif analysisName == 'ngrams':
        # ngram bigram으로 고정
        ngramNum = 2 # data["option2"]
        linkStrength = data["option3"]
        success, result_graph, analysisInfo = ngrams(email, keyword, savedDate, optionList, analysisName, ngramNum, linkStrength)
        if success :
            resultDic = {'returnCode': 200,  #'returnDate' : datetime.datetime.now(), 
            'activity' : analysisName, 'email' : email,
            'keyword' : keyword, 'savedDate' : savedDate,'analysisDate': analysisInfo["analysis_date"], 'option1' : optionList, "option2" : ngramNum, 'option3' : linkStrength, 
            'result_graph': result_graph,
            "jsonDocId": analysisInfo["doc_id"]}
        else:
            resultDic = {'returnCode': 400, 'errMsg': "ngram 분석 실패 \n"+ result_graph}

    
    # for hcluster
    elif analysisName == 'hcluster':
        treeLevel = 5#data["option2"]
        print("고정된 treeLevle로 hcluster 분석 시작합니다.")
        success, result_graph, analysisInfo = hcluster(email, keyword, savedDate, optionList, analysisName, treeLevel)
        print("\n hcluster 분석 결과\n")
        print(result_graph)
        if success :
            resultDic = {'returnCode': 200,  #'returnDate' : datetime.datetime.now(), 
            'activity' : analysisName, 'email' : email,
            'keyword' : keyword, 'savedDate' : savedDate,'analysisDate': analysisInfo["analysis_date"], 'option1' : optionList, "option2" : data["option2"], 
            'result_graph': result_graph,
            "jsonDocId": analysisInfo["doc_id"]}
        else:
            resultDic = {'returnCode': 400, 'errMsg': "계층군집분석 실패 \n"+ result_graph}
        
    # for LDA
    elif analysisName == 'topicLDA':
        app.logger.info(identification + "topicLDA 요청 확인")

        success, result_graph, analysisInfo = topicLDA(email, keyword, savedDate, optionList, analysisName)

        if success :
            resultDic = {'returnCode': 200,  #'returnDate' : datetime.datetime.now(), 
            'activity' : analysisName, 'email' : email,
            'keyword' : keyword, 'savedDate' : savedDate,'analysisDate': analysisInfo["analysis_date"], 'option1' : optionList, 
            'result_graph': result_graph,
            "jsonDocId": analysisInfo["doc_id"]}
        else:
            resultDic = {'returnCode': 400, 'errMsg': "토픽모델링 실패 \n"+ result_graph}
    
    # for word embedding (Word2Vec)
    elif analysisName == 'word2vec':
        app.logger.info(identification + "topicLDA 요청 확인")

        success, result_graph, analysisInfo = word2vec(email, keyword, savedDate, optionList, analysisName)

        if success :
            resultDic = {'returnCode': 200,  #'returnDate' : datetime.datetime.now(), 
            'activity' : analysisName, 'email' : email,
            'keyword' : keyword, 'savedDate' : savedDate,'analysisDate': analysisInfo["analysis_date"], 'option1' : optionList, 
            'result_graph': result_graph,
            "jsonDocId": analysisInfo["doc_id"]}
        else:
            resultDic = {'returnCode': 400, 'errMsg': "토픽모델링 실패 \n"+ result_graph}

    else: 
        return 'result'

    return json.dumps(resultDic, default=json_util.default, ensure_ascii=False)

###################################################################################################################

#################################################
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
from topic_analysis.__get_logger import __get_logger

@app.route('/svm', methods=['GET'])#app객체로 라우팅 경로 설정
def svm():
    #app=Flask(__name__)
    #app.config['JSONIFY_PRETTYPRINT_REGULAR']=True

    now=datetime.datetime.now()
    date=now.strftime('%Y-%m-%d')

    filename='./log/svm.log'
    with open(filename, "a") as f:
        f.write(date)
        f.write("\n")
    print("svm.log에 모델예측 실행 날짜를 기록하였습니다.")
    
    result=SVM.MoEs(date)

    return json.dumps(result, ensure_ascii=False)
@app.route('/train', methods=['GET'])#app객체로 라우팅 경로 설정
def svm_train():
    #app = Flask(__name__)
    #app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

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

#SVM 모델을 훈련시키는 scheduler
sched_train = BackgroundScheduler(daemon=True)
sched_train.add_job(svm_train,'cron',day=1)
#sched_train.add_job(svm_train)
sched_train.start()


#SVM_모델을 실행하는 scheduler
sched = BackgroundScheduler(daemon=True)
#sched.add_job(svm)
sched.add_job(svm,'cron',day=1)
sched.start()

@app.route("/countTable",methods=['POST'])
def countTable():
    # app.logger.info("******/tfidfTable 라우터에서 요청 확인")
    print("******/countTable 라우터에서 요청 확인")
    #app = Flask(__name__)
    #app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    if request.method == 'POST':
            data = request.json 
            get_all = data["get_all"]
    else: 
        return 'GET result'
    if get_all:
        wordCount_all.getAllCountTable()
    else:
        hash_key = data["hash_key"]
        result = wordCount_all.getAllCountTable(hash_key)
        return json.dumps(result, default=json_util.default, ensure_ascii=False)


###################################################################################################################

#sched_train = BackgroundScheduler(daemon=True)
#sched_train.add_job(allTfidfTable)
#sched_train.add_job(multi_SVM_train,'interval',hours=24)
#sched_train.start()
#@app.route("/tfidfTable",methods=['GET'])


#########################################
# 191227 ES Test update : use esFunc module
from common import esFunc
@app.route('/esTest', methods=['GET'])
def esTest():
    result = esFunc.esGetDocs(9)
    
    return json.dumps(result, ensure_ascii=False)

#@app.route('/testRead', methods=['GET'])
def testRead():
    result = esFunc.dataLoad()

    return json.dumps(result, ensure_ascii=False)

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

    # texts = """
    # □ 평화번영을 위한 남북관계 발전방안「6.15공동선언」 이후 남북관계는 빠른 속도로 발전하고 있습니다. 그러나 장기간에 걸친 분단으로 인해 냉전적 사고와 논리, 불신이 남과 북의 관계 진전에 발목을 잡고 있는 것도 사실입니다.공존공영의 남북관계를 정립하기 위해서는 무엇보다 상호신뢰를 쌓기 위한 노력과, 이를 뒷받침할 수 있는 통일교육 지원 등의 국내적 기반 조성도 필요합니다.우리 민주평화통일자문회의 위원들은 한반도의 평화번영을 위한 남북관계의 발전을 위해 다음의 건의를 드립니다.첫 째, 남과 북이 서로 만날 수 있는 기회를 많이 만들어내야 합니다.대구 유니버시아드대회를 통해 우리는 북한 주민들이 우리와 얼마나 다른 사고와 행동을 하는지 생생히 보았습니다.남과 북이 서로를 이해하고 화합하기 위해서는 무엇보다 먼저 많이 만나는 것이 필요합니다.둘 째, 지방자치단체와 시민사회단체 등의 남북교류가 활성화되어야 합니다.남북한 관계가 탄탄한 뿌리를 내리기 위해서는 남과 북을 잇는 다양한 네트워크가 필요합니다. 먼저 지방자치단체간 자매결연을 통한 협력체제를 구축하고, 시민사회단체간에도 연대를 맺는 활동이 필요합니다.이들 상호간의 남북교류는 안정적인 남북관계를 뒷받침하는 든든한 버팀목이 될 수 있을 것입니다.셋 째, 인도주의적 대북지원이 적극적으로 확대되어야 합니다.인도주의 정신에 입각한 대북지원은 정치적 논리를 초월하여 실천해야 할 매우 중요한 과제입니다. 일회성 지원이나 이벤트성 행사보다는 지속적인 지원이 절실히 필요합니다.범국민적 차원에서 폭넓게 펼칠 수 있는 북한에 나무심기 운동, 북한 어린이 돕기운동 등이 좋은 예가 될 수 있을 것입니다.넷 째, 제2차 남북정상회담이 빠른 시일 내에 열리기를 기대합니다.북핵문제 해결 등 한반도의 평화체제 구축을 위한 역사적 전기 마련이 필요한 시점입니다.제2차 정상회담을 통해 보다 밝은 남북관계를 재정립하고, 동북아의 안정에도 기여할 수 있을 것입니다.□ 국민통합과 한민족 통일역량 결집방안한반도에서의 평화와 번영의 성취는 동북아뿐만 아니라 전세계의 평화와 번영에도 긴요하다는 점에서 하루빨리 이루어야 할 민족적 과제입니다. 따라서 7천만 국내외 동포의 통일역량의 결집은 장차 한반도 통일에 결정적 담보가 될 것 입니다.해외동포는 통일을 위한 가교의 역할로, 남북한 주민은 서로를 이해하는 넓은 아량으로 그리고 우리 사회 내부는 겨레가 함께 살아갈 수 있는 의지를 모아 새로운 시대에 새로운 한민족 공동체를 창조하는 데 적극적으로 참여하여야 합니다.우리 민주평화통일자문회의 위원들은 국민대통합과 한민족의 통일역량 결집을 위해 다음의 건의를 드립니다.첫 째, 분단의 결과로 생긴 민족내부의 차이와 갈등을 폭넓게 수용하는 정책이 필요합니다.냉전적 사고에 사로잡힌 불신과 대결로는 민족의 통일역량을 결집할 수 없습니다. 다양한 의견과 차이를 인정하고 이를 공존의 기초로 받아들이는 포용의 자세가 필요합니다.국내는 물론 현지사회에 동화된 한민족의 일원도 차이와 갈등을 넓게 아우르는 민족대통합의 정책이 필요합니다.둘 째, 한민족 경제·문화 공동체를 만들어 민족상생의 시대를 열어야 합니다.세계화 시대에 각 나라에 거주하는 해외동포들이 경제·사회적으로 주류에 서서 한민족의 정체성을 유지할 수 있도록, 그리고 현지 국민들과 융화하면서 자긍심을 유지·발전시킬 수 있도록 지원해야 합니다.한민족 경제·문화공동체를 형성하기 위해 현지 한국어 교육의 강화, 청년세대의 상호 교류, 지역사회내의 다양한 네트워크 형성으로 한민족의 정체성을 강화하여야 합니다.또한 현지 국민들과의 융화를 위해 이미 설립되어 있거나 설립해야 할 「한국 문화센터」에 지원을 아끼지 말아야 합니다.셋 째, 민주평통 해외자문위원의 역할을 강화할 필요가 있습니다.동북아 중심국가로 성장하는 통일한국의 건설에는 국민대통합과 함께 해외동포의 역량결집이 대단히 중요합니다. 특히 한민족의 10% 이상인 7백만이 해외에 살고 있다는 점은 큰 자산이라 할 수 있습니다.해외동포의 통일역량을 효과적으로 결집하는 데 민주평통 해외위원의 참여와 역할이 대단히 중요한 비중을 차지하고 있습니다. 이를 위한 제도적 장치가 시급히 마련되어야 합니다.
    # """

    # with open("krWl.txt", "r" ,encoding='utf-8') as f:
    #     texts = f.read() 
        # print(f.read())
        # tokenized_doc = tagger.nouns(texts)
        # tokenized_doc = ' '.join(tokenized_doc) 
        # print("형태소 분석 이후 단어 토큰의 개수",len(tokenized_doc)) 

    # result = keywords(tokenized_doc, words = 15 , scores=True)
    result = keywords(tokenized_doc)

    # with open(DIR_FE, 'w', -1, "utf-8") as f:
    with open("./wrCul.json", 'w', -1, "utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    return json.dumps(result, ensure_ascii=False)

def wordRank():
    #Retreive text from elasticsearch
    results = es.get(index=INDEX, doc_type='nkdb', id='5dc9fc5033ec463330e97e94')
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
        # print("query body has been built!")
        res = es.search(index=INDEX, body=allDocs)
        # print(res)

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
        # print("ready to search")
        res = es.search(index=INDEX, body=searchDocs)
        print(res)
        numOfDocs = res["hits"]["total"]["value"]
        searchDataArr.append(numOfDocs)

        # print(numOfDocs)

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

    res = es.search(index=INDEX, body=body)

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
#         dic["label"]=wordkeyword
#         result.append(dic)
#         dic={}

#     return result

@app.after_request
def after_request(response):

    # response.headers.add('Access-Control-Allow-Origin', '*')
    # response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


# 21.08.17 add error handling
from flask import json
from werkzeug.exceptions import HTTPException

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

import account.BEMiddleware as BEMW

if __name__ == "__main__": # 다른 코드에 import되어있을 경우에는 실행되지 않도록 함

    # flask run(실행하면 port를 정해줄수 있다.
    # 가릴 수 있도록 변수 형식으로 불러오기.
 
    context=(kubic_ssl.crt,kubic_ssl.key) #gitignore 비밀경로
    app.run(host=BEMW.hostIP, port=BEMW.port, ssl_context=context)   
    # app.run(host=BEMW.hostIP, port=BEMW.port, ssl_context=context, debug=True)   
