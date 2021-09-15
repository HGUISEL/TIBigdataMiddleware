from pymongo import MongoClient
import datetime
from dateutil import parser
import pandas as pd
import json
from konlpy.tag import Mecab

#from TextMining.Tokenizer.kubic_data import *

client = MongoClient('localhost', 27017)
db = client.user
def getMyDocByEmail2(email, keyword, savedDate):
    try:
        savedDate = datetime.datetime.strptime(savedDate, "%Y-%m-%dT%H:%M:%S.%fZ") 
    except Exception as e:
        return 'failed', "getMyDocByEmail2: savedDate가 형식에 맞지 않습니다.  " + str(e)
    #print(savedDate)

    doc = db.mydocs.find_one({"userEmail": email})
    #print(doc)
    docList = []
    try:
        for idx in range(len(doc['keywordList'])):
            #print(doc['keywordList'][idx])
            docList.append(doc['keywordList'][idx])
            if docList[idx]['keyword'] == keyword and docList[idx]['savedDate'] == savedDate:#datetime.datetime.strptime(savedDate, "%Y-%m-%dT%H:%M:%S.%fZ"):
                #print("저장된 도큐먼트 id: ", docList[idx]['savedDocHashKeys'])
                return docList[idx]['savedDocHashKeys']
    except Exception as e:
        return 'failed', "getMyDocByEmail2: mongo에 내보관함 데이터가 없습니다. " + str(e)

#getMyDocByEmail2('21600280@handong.edu', '북한', "2021-07-08T11:46:03.973Z")
#getMyDocByEmail2('21800409@handong.edu', '북한', "2021-08-04T03:48:54.395Z")

# 해킹대비 mongodb에 저장된 회원가입한 이메일인지 확인
def checkEmail(email):
    if db.users.find( {'email': email}).count() == 0 :
        print("등록된 회원 이메일이 아닙니다.")
        return False
    else:
        print("회원확인이 완료되었습니다.")
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
    doc = dbTM.usersDic.find({"userEmail": email, "keyword": keyword, 'savedDate': savedDate})
    json_stopfile = json.dumps(doc[0]['stopword'], ensure_ascii=False)
    dict_stopfile = json.loads(json_stopfile)
    print("DB에 저장된 stopword파일입니다.\n", dict_stopfile)  

    # 불용어사전 형식오류시 False반환
    for key, value in dict_stopfile.items():
        if key == '':
            return False
    return dict_stopfile
#getStopword("21600280@handong.edu", '북한', "2021-07-08T11:46:03.973Z")
   
def getSynonym(email, keyword, savedDate): # ,json_file):
    doc = dbTM.usersDic.find({"userEmail": email, "keyword": keyword, 'savedDate': savedDate})
    json_synfile = json.dumps(doc[0]['synonym'], ensure_ascii=False)
    dict_synfile = json.loads(json_synfile)
    print("DB에 저장된 synonym파일입니다.\n", dict_synfile)  

    # 유의어사전 형식오류시 False반환
    for key, value in dict_synfile.items():
        #print(key, value)
        if key == '' or value == '':
            return False
    return dict_synfile
#getSynonym("21600280@handong.edu", '북한', "2021-07-08T11:46:03.973Z")

def getCompound(email, keyword, savedDate):
    doc = dbTM.usersDic.find({"userEmail": email, "keyword": keyword}) #, 'savedDate': savedDate})
    json_compfile = json.dumps(doc[0]['compound'], ensure_ascii=False)
    dict_compfile = json.loads(json_compfile)
    #return dict_compfile
    
    mecabPosList = ['NNG', 'NNP', 'NNB', 'NNBC', 'NR', 'NP', 'VV', 'VA', 'VX', 'VCP', 'VCN', 'MM', 'MAG', 'MAJ', 
    'IC', 'JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'JX', 'JC', 'EP', 'EF', 'EC', 'ETN', 'XPN', 'XSN',
    'XSV', 'XSA', 'XR', 'SF', 'SE', 'SSO', 'SSC', 'SC', 'SY', 'SL', 'SH', 'SN']
    
    # 복합어사전 형식오류시 False반환
    # for key, value in dict_compfile.items():
    #     #print(key, value)
    #     if key == '' or value == '' or value not in mecabPosList:
    #         return False
    #     else:
    #         return dict_compfile
    
    print("DB에 저장된 compound파일입니다.\n", dict_compfile) 
    return dict_compfile  

#getCompound("21600280@handong.edu", '북한', "2021-07-08T11:46:03.973Z")
#getCompound("default","", "")

def getPreprocessing(email, keyword, savedDate, optionList):
    doc = dbTM.preprocessing.find_one({"userEmail":email, "keyword":keyword, "savedDate":savedDate})# saved date issue
    return doc['tokenList'], doc['nTokens']

def getPreprocessingAddTitle(email, keyword, savedDate, optionList):
    doc = dbTM.preprocessing.find_one({"userEmail":email, "keyword":keyword, "savedDate":savedDate, "addTitle" : "Yes"})# saved date issue
    return doc['tokenList'], doc['titleList'], doc['nTokens']

#print(getPreprocessing('21600280@handong.edu', '북한', "2021-07-08T11:46:03.973Z", 30)[0])

def getCount(email, keyword, savedDate, optionList):
    # for analysisDate : datetime.datetime.strptime(savedDate[:-1], "%Y-%m-%d %H:%M:%S.%f"
    doc = dbTM.count.find_one({"userEmail":email, "keyword":keyword, "savedDate": savedDate})
    print(doc["_id"]) # 카운트가 없으면 먼저 카운트 하라고 말해줘야함.
    try:
        str(doc['resultJson'])
        return doc['resultJson'], doc['nTokens']
    except:
        return doc["result_table"], doc['nTokens']

#getCount('21800520@handong.edu', '북한', "2021-08-10T10:59:29.974Z", 30)