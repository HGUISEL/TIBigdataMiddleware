from pymongo import MongoClient
import datetime
from dateutil import parser
import pandas as pd
import json
from konlpy.tag import Mecab

from TextMining.Tokenizer.kubic_data import *

client = MongoClient('localhost', 27017)
db = client.user
def getMyDocByEmail2(email, keyword, savedDate):
    savedDate = datetime.datetime.strptime(savedDate, "%Y-%m-%dT%H:%M:%S.%fZ") 
    #print(savedDate)
    doc = db.mydocs.find_one({"userEmail": email})
    #print(doc)
    docList = []

    for idx in range(len(doc['keywordList'])):
        #print(doc['keywordList'][idx])
        docList.append(doc['keywordList'][idx])
        if docList[idx]['keyword'] == keyword and docList[idx]['savedDate'] == savedDate:#datetime.datetime.strptime(savedDate, "%Y-%m-%dT%H:%M:%S.%fZ"):
            #print("저장된 도큐먼트 id: ", docList[idx]['savedDocHashKeys'])
            return docList[idx]['savedDocHashKeys']

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
    return dict_compfile

def tfidf(email, keyword, savedDate, optionList, analysisName):
    corpus = search_in_mydoc2(email, keyword, savedDate)['all_content'].tolist()    #문장으로 이루어진 doc
    nTokens = optionList
    #print("corpus\n", corpus, "\nNumber of Doc: ",len(corpus))
    top_words = getCount(email, keyword, savedDate, optionList)[0]
    top_words = json.loads(top_words)
    
    tfidf_vectorizer = TfidfVectorizer().fit(top_words)
    feature_names = tfidf_vectorizer.get_feature_names()

    df = pd.DataFrame(tfidf_vectorizer.transform(corpus).toarray(), columns=feature_names)
    words = tfidf_vectorizer.get_feature_names()
    print("Tfidf 단어사전\n",words)
    print("Tfidf 결과\n", df)    
    
    df_T = df.T.sum(axis=1)
    #df_T['word'] = words
    #df_T['rate']= df.T.sum(axis=1) #단어별 tfidf 합친 값
    #df_T = df_T[['word', 'rate']]
    
    print(df_T.index, df_T.values)
    
    ## Barchart 그리기
    FONT_PATH='TextMining/NanumBarunGothic.ttf'
    fontprop = fm.FontProperties(fname=FONT_PATH, size=8)
    plt.figure(figsize=(20,5))
    plt.bar(df_T.index, df_T.values)
    plt.xticks(rotation=40, ha='right', fontproperties=fontprop)
    print("tfidf barchart 결과파일이 생성되었습니다..")
    plt.savefig('tfidf_barchart.jpg')

    ## Wordcloud 시각화
    Cloud = WordCloud(font_path = FONT_PATH,background_color="white", max_words=50).generate_from_frequencies(df_T)
    print("tfidf wordcloud 결과파일이 생성되었습니다..")
    Cloud.to_file('tfidf_wordcloud.jpg')
    
    #Mongo에 저장된 바차트, 워드클라우드의 binary 파일과 이미지파일이 일치하는지 length를 통해 확인
    from os.path import getsize
    BarFile = 'tfidf_barchart.jpg'    
    WcFile = 'tfidf_wordcloud.jpg'
    bar_file_size = getsize(BarFile)
    wc_file_size = getsize(WcFile)
    
    print('File Name: %s \tFile Size: %d' %(BarFile, bar_file_size))
    print('File Name: %s \tFile Size: %d' %(WcFile, wc_file_size))

    
    ### Mongo 저장 ### 
    client=MongoClient(host='localhost',port=27017)
    #print('MongoDB에 연결을 성공했습니다.')
    db=client.textMining
    nTokens = optionList
    now = datetime.datetime.now()
    #print("time: ", now,'\n', now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")) #형식
    
    '''
    ## 몽고db에 Barchart 이미지 binary로 저장
    print("\nMongoDB에 Tfidf 분석 결과를 바차트로 저장합니다.")
    fs = gridfs.GridFS(db, 'tfidf') #tfidf.files, tfidf.chunks로 생성됨
    with open(BarFile, 'rb') as f:
        contents = f.read()
    fs.put(contents, filename='tfidf_bar')

    ## 몽고db에 WordCloud 이미지 binary로 저장
    print("MongoDB에 Tfidf 분석 결과를 wordcloud로 저장합니다.\n")
    with open(WcFile, 'rb') as f:
        contents = f.read()
    fs.put(contents, filename='tfidf_wordcloud')

    barBinary = getBinaryImage(bar_file_size, analysisName)
    wcBinary = getBinaryImage(wc_file_size, analysisName)

    doc={
        "userEmail" : email,
        "keyword" : keyword,
        "savedDate": savedDate,
        "analysisDate" : datetime.datetime.now(),
        #"duration" : ,
        "nTokens" : nTokens,
        "resultJson" : json.dumps(dict(df_T), ensure_ascii=False),
        "resultBar" : barBinary,
        "resultWC" : wcBinary
        #"resultCSV":
    }
    db.tfidf.insert_one(doc)  

    print("MongoDB에 저장되었습니다.")
    '''
    return df

#tfidf('sujinyang@handong.edu', '북한', "2021-07-08T11:46:03.973Z", 100, 'tfidf')
#tfidf('21600280@handong.edu', '통일', "2021-07-08T11:46:03.973Z", 100, 'tfidf')
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

#print(getPreprocessing('21600280@handong.edu', '북한', "2021-07-08T11:46:03.973Z", 30)[0])

def getCount(email, keyword, savedDate, optionList):
    doc = dbTM.count.find_one({"userEmail":email, "keyword":keyword, "savedDate":savedDate})
    return doc['resultJson'], doc['nTokens']

#print(getCount('21600280@handong.edu', '북한', "2021-07-08T11:46:03.973Z", 30)[0])