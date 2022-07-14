import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname('TextMining/Analyzer'))))
from pymongo import MongoClient
import datetime
from dateutil import parser
import pandas as pd
import json
from konlpy.tag import Mecab
import account.MongoAccount as monAcc

import logging
import traceback

#from TextMining.Tokenizer.kubic_data import *

client = MongoClient(monAcc.host, monAcc.port)
db = client.user
logger = logging.getLogger("flask.app.mystorage")

def getMyDocByEmail2(email, keyword, savedDate):
    try:
        savedDate = datetime.datetime.strptime(savedDate, "%Y-%m-%dT%H:%M:%S.%fZ") 
    except Exception as e:
        return ('failed', "getMyDocByEmail2: savedDate가 형식에 맞지 않습니다.  " + str(e))
    #print(savedDate)

    doc = db.mydocs.find({"userEmail": email}).sort("_id", -1).limit(1)
    #print(doc)
    doc = doc[0]
    docList = []
    try:
        for idx in range(len(doc['keywordList'])):
            #print(doc['keywordList'][idx])
            docList.append(doc['keywordList'][idx])
            if docList[idx]['keyword'] == keyword and docList[idx]['savedDate'] == savedDate:#datetime.datetime.strptime(savedDate, "%Y-%m-%dT%H:%M:%S.%fZ"):
                #print("저장된 도큐먼트 id: ", docList[idx]['savedDocHashKeys'])
                return docList[idx]['savedDocHashKeys']
    except Exception as e:
        return ('failed', "getMyDocByEmail2: mongo에 내보관함 데이터가 없습니다. " + str(e))

#getMyDocByEmail2('21600280@handong.edu', '북한', "2021-07-08T11:46:03.973Z")
#getMyDocByEmail2('21800409@handong.edu', '북한', "2021-08-04T03:48:54.395Z")

# 해킹대비 mongodb에 저장된 회원가입한 이메일인지 확인
def checkEmail(email):
    if db.users.find( {'email': email}).count() == 0 :
        logger.error(identification + "등록된 회원 이메일이 아닙니다.")
        return False
    else:
        logger.info("회원확인이 완료되었습니다.")
        return True

dbTM = client.textMining

# 저장된 Image파일(barchart, wordcloud): length로 image id 매치해서 binary가져오기 
def getBinaryImage(leng, analysisName):
    if analysisName == 'count':
        doc_files = dbTM.count.files.find_one({'length': leng})
        doc_chunks = dbTM.count.chunks.find_one({'files_id': doc_files['_id']})
    elif analysisName == 'tfidf':
        doc_files = dbTM.tfidf.files.find_one({'length': leng})
        doc_chunks = dbTM.tfidf.chunks.find_one({'files_id': doc_files['_id']})
    return doc_chunks['data']

#사용자사전 get 함수(json 읽어서 dict로 return)
def getStopword(email, keyword, savedDate): # ,json_file):
    doc = dbTM.usersDic.find({"userEmail": email})
    json_stopfile = json.dumps(doc[0]['stopword'], ensure_ascii=False)
    dict_stopfile = json.loads(json_stopfile)
    # print("DB에 저장된 stopword파일입니다.\n", dict_stopfile)  

    # 불용어사전 형식오류시 False반환
    for key, value in dict_stopfile.items():
        if key == '':
            return False
    return dict_stopfile
#getStopword("21600280@handong.edu", '북한', "2021-07-08T11:46:03.973Z")
   
def getSynonym(email, keyword, savedDate): # ,json_file):
    doc = dbTM.usersDic.find({"userEmail": email})
    json_synfile = json.dumps(doc[0]['synonym'], ensure_ascii=False)
    dict_synfile = json.loads(json_synfile)
    # print("DB에 저장된 synonym파일입니다.\n", dict_synfile)  

    # 유의어사전 형식오류시 False반환
    for key, value in dict_synfile.items():
        if str(type(key)) !="<class 'str'>" or str(type(value)) != "<class 'list'>":
            return False

        key = key.strip()
        valList = []
        for val in value:
            valList.append(val.strip())
        value = valList

        if key == '' or value == '':
            return False
    return dict_synfile
#getSynonym("21600280@handong.edu", '북한', "2021-07-08T11:46:03.973Z")

def getCompound(email, keyword, savedDate):
    try:
        identification = str(email)+'_'+'preprocessing(stop_syn)'+'_'+str(savedDate)+"// "
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification + '로깅 설정오류: '+ str(err))
        return False
    try:
        doc = dbTM.usersDic.find({"userEmail": email}) #, 'savedDate': savedDate})
        json_compfile = json.dumps(doc[0]['compound'], ensure_ascii=False)
        dict_compfile = json.loads(json_compfile)
        #return dict_compfile
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification + '사전 파일 읽기 오류: '+ str(err))
        return False
    try:
        mecabPosList = ['NNG', 'NNP', 'NNB', 'NNBC', 'NR', 'NP', 'VV', 'VA', 'VX', 'VCP', 'VCN', 'MM', 'MAG', 'MAJ', 
        'IC', 'JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'JX', 'JC', 'EP', 'EF', 'EC', 'ETN', 'XPN', 'XSN',
        'XSV', 'XSA', 'XR', 'SF', 'SE', 'SSO', 'SSC', 'SC', 'SY', 'SL', 'SH', 'SN']

        # 프론트엔드 오류로 인한 수정코드
        # print(dict_compfile) # db에서 찾은 사전 확인
        newdict = dict()
        for key, value in dict_compfile.items():
            key = key.strip()
            # print(type(value))
            # FE에서 csv를 저장할 떄 태그 이름을 리스트 안에 저장하는 오류 방지용
            if str(type(value)) == "<class 'list'>" and len(value) > 0:
                value = value[0]
            if str(type(value)) == "<class 'str'>":
                value = value.strip()
            else:
                logger.info(identification,key,value,"이(가) 복합어 형식에 맞지 않아 제거되었습니다.")
                continue
            # 파일에 공백이 있는 경우 저장안하고 넘김(패스). 프론트엔드 차원에서 한번 더 확인 해야할 필요 있음.
            # 파일에 공백이 아닌경우 공백제거 후 사전에 저장
            if key == '' or value == '':
                pass
            else:
                newdict[key] = value.strip()
        dict_compfile = newdict

        #복합어사전 형식오류시 False반환
        for key, value in dict_compfile.items():
            # print(key, value)
            if value not in mecabPosList:
                return False
        logger.info("최종 적용될 복합어사전: \n", newdict)
        return dict_compfile
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification + '불러온 파일을 형식에 맞게 저장하는 중 오류발생: '+ str(err))
        return False

#getCompound("21800520@handong.ac.kr", '북한', "2021-07-08T11:46:03.973Z")
#getCompound("default","", "")

def getPreprocessing(email, keyword, savedDate, optionList):
    docs = dbTM.preprocessing.find({"userEmail":email, "keyword":keyword, "savedDate":savedDate}).sort("_id", -1).limit(1)# saved date issue
    # print(email, keyword, savedDate)
    # print(docs[0]['titleList'])
    return docs[0]['tokenList'], docs[0]['nTokens']

def getPreprocessingAddTitle(email, keyword, savedDate, optionList):
    doc = dbTM.preprocessing.find({"userEmail":email, "keyword":keyword, "savedDate":savedDate, "addTitle" : "Yes"}).sort("_id", -1).limit(1)# saved date issue
    return doc[0]['tokenList'], doc[0]['titleList'], doc[0]['nTokens']

#print(getPreprocessing('21600280@handong.edu', '북한', "2021-07-08T11:46:03.973Z", 30)[0])

def getCount(email, keyword, savedDate, optionList):
    # for analysisDate : datetime.datetime.strptime(savedDate[:-1], "%Y-%m-%d %H:%M:%S.%f"
    doc = dbTM.count.find({"userEmail":email, "keyword":keyword, "savedDate": savedDate}).sort("_id", -1).limit(1)
    if doc is None:
        return None
     # 카운트가 없으면 먼저 카운트 하라고 말해줘야함.

    try:
        str(doc[0]['resultJson'])
        return doc[0]['resultJson'], doc[0]['nTokens']
    except:
        return doc[0]["result_table"], doc[0]['nTokens']

#getCount('21800520@handong.edu', '북한', "2021-08-10T10:59:29.974Z", 30)