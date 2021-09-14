from posixpath import join
import sys, os
from numpy.lib.npyio import save
import urllib3
import datetime
from numpy.core.numeric import NaN
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname('TextMining/Tokenizer'))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname('TextMining/Analyzer'))))

import subprocess
import pandas as pd
from numpy.core.fromnumeric import shape
from TextMining.Tokenizer.kubic_data import *
from TextMining.Tokenizer.kubic_mystorage import *
import pandas as pd
from konlpy.tag import Mecab
from jamo import h2j, j2hcj
import re
 
## Morphological analysis(형태소 분석)
from konlpy.tag import Kkma

# 전처리 & 불용어사전적용
def stop_syn(email, keyword, savedDate, mecab, wordclass, stopwordTF, synonymTF):
#def stop_syn(email, keyword, savedDate, mecab, wordclass): 
    print("전처리를 시작합니다")
    datas = search_in_mydoc2(email, keyword, savedDate)
    print("data2: ", datas)
    nDocs = len(datas)
    
    if stopwordTF == True:
      stopword_file = getStopword(email, keyword, savedDate)
    else:
      stopword_file = getStopword('default','', '')

    if synonymTF == True:
      synonym_file = getSynonym(email, keyword, savedDate)
    else:
      synonym_file = getSynonym('default','', '')

    # stopword_file = getStopword(email, keyword, savedDate) #사용자가 등록한 불용어
    # synonym_file = getSynonym(email, keyword, savedDate) #사용자가 등록한 유의어
    
    #####err
    '''
    for i in range(len(datas['all_content'])):
        datas.loc[i,'all_content'] = Kkma().sentences(datas['all_content'][i])
    print(datas[:100])
    '''

    # 형태소추출
    resultList = []   
    #datas = datas[0:1]
    for i in range(len(datas['all_content'])):
        posList=[]
        tokenToAnalyze=[]

        poss = mecab.pos(datas['all_content'][i])
        # datas['result'] = posList
        # print(poss[:100])

        for token, pos in poss:
            if wordclass[0]=='1' and pos == 'VV': # 동사만
                tokenToAnalyze.append(token)
            if wordclass[1]=='1' and pos.startswith('N'): # 명사
                tokenToAnalyze.append(token)
            if wordclass[2]=='1' and pos == 'VA': # 형용사 
                tokenToAnalyze.append(token)
        
        #print("저장된 토큰\n", tokenToAnalyze)

    # 불용어처리
        if(stopword_file != False):
            for j in range(len(tokenToAnalyze)):
                if tokenToAnalyze[j] not in stopword_file:
                    posList.append(tokenToAnalyze[j]) ############
        else:
            return False, "불용어사전 형식 오류"
            #print("전처리 결과\n", posList[:100])
        resultList.append(posList)
    
    #print('\n유의어, 복합어사전 적용 전: ', resultList[0][20000:20100]) #16 이메일
    print('\n유의어, 복합어사전 적용 전: ', resultList[0][1700:1900]) ##### 

    #유의어를 json형식으로 받고 dict 이용(split필요x)
    if(synonym_file != False):
        syn_df = pd.DataFrame(synonym_file)
        #print("유의어사전\n", syn_df, len(syn_df), len(syn_df.columns), syn_df.columns[0])
        #print("[0,1]", syn_df.iloc[0,1], " [0,2]", syn_df.iloc[0,2], "[1,0]", syn_df.iloc[1,0], " [1,1]", syn_df.iloc[1,1], " [1,2]", syn_df.iloc[1,2])
       
        #result = resultList[0]        
        #print("유의어사전 적용 전:", resultList[0][200:300], len(resultList[0]))
        for ri in resultList[0:1]: #doc개수
            for i in range(len(syn_df)):
                for j in range(len(syn_df.columns)):
                    for k in range(len(ri)): 
                        if ri[k] == syn_df.iloc[i,j]:
                            print(k, "번째, ", "**유의어 \"" ,ri[k] , "\"(을)를 찾았습니다. \"", syn_df.columns[i], '\"(으)로 변경합니다.')
                            ri[k] = syn_df.columns[i]   
        #print("\n유의어사전 적용 후:", resultList[0][200:300], len(resultList[0]))
    else:
        return False, "유용어사전 형식 오류"

    return True, resultList
 
# 사용자사전적용(복합어)   
def get_jongsung_TF(sample_word): 
  sample_text_list = list(sample_word) 
  last_word = sample_text_list[-1] 
  last_word_jamo_list = list(j2hcj(h2j(last_word))) 
  last_jamo = last_word_jamo_list[-1] 
  jongsung_TF = "T" 
  if last_jamo in ['ㅏ', 'ㅑ', 'ㅓ', 'ㅕ', 'ㅗ', 'ㅛ', 'ㅜ', 'ㅠ', 'ㅡ', 'ㅣ', 'ㅘ', 'ㅚ', 'ㅙ', 'ㅝ', 'ㅞ', 'ㅢ', 'ㅐ','ㅔ', 'ㅟ', 'ㅖ', 'ㅒ']: 
    jongsung_TF = "F" 
  return jongsung_TF

#file not found error
def compound(email, keyword, savedDate, wordclass, stopwordTF, synonymTF, compoundTF):
#def compound(email, keyword, savedDate, wordclass): 
    file_data = []
    print(email, '\t', keyword, '\t', savedDate, '에 대한 전처리를 진행합니다.')

    if compoundTF == True:
      compound_file = getCompound(email, keyword, savedDate)  #사용자가 등록한 사전 적용
    else:
      compound_file = getCompound("default","", "")  # 지정해놓은 default 사용자사전 적용
  
    if(compound_file != False):
        com_df = pd.DataFrame(list(compound_file.items()), columns=['단어', '품사'])
        for idx in range(len(com_df)): 
            jongsung_TF = get_jongsung_TF(com_df['단어'][idx]) 
            line = '{},,,,{},*,{},{},*,*,*,*,*\n'.format(com_df['단어'][idx], com_df['품사'][idx], jongsung_TF, com_df['단어'][idx]) 
            file_data.append(line)
    else:
        return False, "복합어사전 형식 오류"
 
    with open("/home/dapi2/TIBigdataMiddleware/TextMining/mecab-ko-dic-2.1.1-20180720/user-dic/my-dic.csv", 'w', encoding='utf-8') as f: 
        for line in file_data: 
            f.write(line)
 
    class cd:
        def __init__(self, newPath):
            self.newPath = os.path.expanduser(newPath)
 
        def __enter__(self):
            self.savedPath = os.getcwd()
            os.chdir(self.newPath)
 
        def __exit__(self, etype, value, traceback):
            os.chdir(self.savedPath)
    
    with cd("~/TIBigdataMiddleware/TextMining/mecab-ko-dic-2.1.1-20180720"):
        
        #subprocess.call("ls")
        print("\n<<add-userdic.sh>>")
        subprocess.call("ls")

        # subprocess.run('./autogen.sh')
        # subprocess.call("make")

        subprocess.run("./tools/add-userdic.sh") #####error my-dic.csv을 메캅ko안에 
        subprocess.call("ls")

        print("\n<<make install>>")
        subprocess.call(["make", "install", 'DESTDIR=../userlocallibmecab/'])
    
    # usr 권한이 없어 사용 불가능하기 때문에, /home/dapi2/TIBigdataMiddleware/TextMining/userlocallibmecab 을 새로 만들고 사용
    # make install 시에 DESDIR 지정
    mecab = Mecab('/home/dapi2/TIBigdataMiddleware/TextMining/userlocallibmecab/usr/local/lib/mecab/dic/mecab-ko-dic') #/usr/local/lib/mecab/dic/mecab-ko-dic을 자동으로 참조
   
    #success, doc = stop_syn(email, keyword, savedDate, mecab, wordclass)
    success, doc = stop_syn(email, keyword, savedDate, mecab, wordclass, stopwordTF, synonymTF)

    
    print("전처리 결과: ", doc[0][1700:1900]) #동사, 형용사 --> 추출한 개수가 적기 때문에 출력안됨
    #print("전처리 결과 [0]번째 doc: ", doc[0][1700:1800])
    #print("전처리 결과 [1]번째 doc: ", doc[1][1700:1800])

    #nTokens: 전처리 토큰개수
    nTokens=0
    for i in range(len(doc)):
        for j in range(len(doc[i])):
            length = len(doc[i])
        nTokens = length + nTokens
    #print(nTokens)

    if success == True:
    # 사용자사전 test code, true일때만
    # 사용자사전: 신조어일 경우, 띄어쓰기로 분리되어 있는 복합어
        alltokens = [t for tlist in doc for t in tlist]

        for user_word in com_df['단어']:
            if not (user_word in alltokens):
                print(user_word, 'is missing')
        
        # Mongodb 저장
        client=MongoClient(host='localhost',port=27017)
        # print('MongoDB에 연결을 성공했습니다.')
        db=client.textMining

        mdoc={
        "userEmail" : email,
        "keyword" : keyword,
        "savedDate": savedDate,
        "processedDate": datetime.datetime.now(),
        #"duration" : ,
        #"nDocs" : nDocs,
        "nTokens" : nTokens,
        "tokenList" : doc
        }
        db.preprocessing.insert(mdoc)

        print('MongoDB에 저장 되었습니다.')

    return success, doc[0][:100] #전체 형태소 분석한 단어들의 목록 (kubic 미리보기에 뜨도록)
    
#compound('21800409@handong.edu', '북한', "2021-08-04T03:48:54.395Z", '010', False, False, False)[1]

def stop_syn_add_title(email, keyword, savedDate, mecab, wordclass, stopwordTF, synonymTF):
    print("전처리를 시작합니다")
    datas = search_in_mydoc2_add_title(email, keyword, savedDate)
    print("data2: ", datas)
    nDocs = len(datas)
    
    if stopwordTF == True:
      stopword_file = getStopword(email, keyword, savedDate)
    else:
      stopword_file = getStopword('default','', '')

    if synonymTF == True:
      synonym_file = getSynonym(email, keyword, savedDate)
    else:
      synonym_file = getSynonym('default','', '')

    # stopword_file = getStopword(email, keyword, savedDate) #사용자가 등록한 불용어
    # synonym_file = getSynonym(email, keyword, savedDate) #사용자가 등록한 유의어
    
    #####err
    '''
    for i in range(len(datas['all_content'])):
        datas.loc[i,'all_content'] = Kkma().sentences(datas['all_content'][i])
    print(datas[:100])
    '''

    # 형태소추출
    resultList = []   
    #datas = datas[0:1]
    for i in range(len(datas['all_content'])):
        posList=[]
        tokenToAnalyze=[]

        poss = mecab.pos(datas['all_content'][i])
        # datas['result'] = posList
        # print(poss[:100])

        for token, pos in poss:
            if wordclass[0]=='1' and pos == 'VV': # 동사만
                tokenToAnalyze.append(token)
            if wordclass[1]=='1' and pos.startswith('N'): # 명사
                tokenToAnalyze.append(token)
            if wordclass[2]=='1' and pos == 'VA': # 형용사 
                tokenToAnalyze.append(token)
        
        #print("저장된 토큰\n", tokenToAnalyze)

    # 불용어처리
        if(stopword_file != False):
            for j in range(len(tokenToAnalyze)):
                if tokenToAnalyze[j] not in stopword_file:
                    posList.append(tokenToAnalyze[j]) ############
        else:
            return False, "불용어사전 형식 오류"
            #print("전처리 결과\n", posList[:100])
        resultList.append(posList)
    
    #print('\n유의어, 복합어사전 적용 전: ', resultList[0][20000:20100]) #16 이메일
    print('\n유의어, 복합어사전 적용 전: ', resultList[0][1700:1900]) ##### 

    #유의어를 json형식으로 받고 dict 이용(split필요x)
    if(synonym_file != False):
        syn_df = pd.DataFrame(synonym_file)
        #print("유의어사전\n", syn_df, len(syn_df), len(syn_df.columns), syn_df.columns[0])
        #print("[0,1]", syn_df.iloc[0,1], " [0,2]", syn_df.iloc[0,2], "[1,0]", syn_df.iloc[1,0], " [1,1]", syn_df.iloc[1,1], " [1,2]", syn_df.iloc[1,2])
       
        #result = resultList[0]        
        #print("유의어사전 적용 전:", resultList[0][200:300], len(resultList[0]))
        for ri in resultList[0:1]: #doc개수
            for i in range(len(syn_df)):
                for j in range(len(syn_df.columns)):
                    for k in range(len(ri)): 
                        if ri[k] == syn_df.iloc[i,j]:
                            print(k, "번째, ", "**유의어 \"" ,ri[k] , "\"(을)를 찾았습니다. \"", syn_df.columns[i], '\"(으)로 변경합니다.')
                            ri[k] = syn_df.columns[i]   
        #print("\n유의어사전 적용 후:", resultList[0][200:300], len(resultList[0]))
    else:
        return False, "유용어사전 형식 오류"
    
    if len(resultList) == len(datas['post_title']):
        textDict = dict()
        textDict["title"] = datas['post_title']
        textDict['content'] = resultList
            
    return True, textDict


def compound_add_text(email, keyword, savedDate, wordclass, stopwordTF, synonymTF, compoundTF):
#def compound(email, keyword, savedDate, wordclass): 
    file_data = []
    print(email, '\t', keyword, '\t', savedDate, '에 대한 전처리를 진행합니다.')

    if compoundTF == True:
      compound_file = getCompound(email, keyword, savedDate)  #사용자가 등록한 사전 적용
    else:
      compound_file = getCompound("default","", "")  # 지정해놓은 default 사용자사전 적용
  
    if(compound_file != False):
        com_df = pd.DataFrame(list(compound_file.items()), columns=['단어', '품사'])
        for idx in range(len(com_df)): 
            jongsung_TF = get_jongsung_TF(com_df['단어'][idx]) 
            line = '{},,,,{},*,{},{},*,*,*,*,*\n'.format(com_df['단어'][idx], com_df['품사'][idx], jongsung_TF, com_df['단어'][idx]) 
            file_data.append(line)
    else:
        return False, "복합어사전 형식 오류"
 
    with open("/home/dapi2/TIBigdataMiddleware/TextMining/mecab-ko-dic-2.1.1-20180720/user-dic/my-dic.csv", 'w', encoding='utf-8') as f: 
        for line in file_data: 
            f.write(line)
 
    class cd:
        def __init__(self, newPath):
            self.newPath = os.path.expanduser(newPath)
 
        def __enter__(self):
            self.savedPath = os.getcwd()
            os.chdir(self.newPath)
 
        def __exit__(self, etype, value, traceback):
            os.chdir(self.savedPath)
    
    with cd("~/TIBigdataMiddleware/TextMining/mecab-ko-dic-2.1.1-20180720"):
        
        #subprocess.call("ls")
        print("\n<<add-userdic.sh>>")
        subprocess.call("ls")

        # subprocess.run('./autogen.sh')
        # subprocess.call("make")

        subprocess.run("./tools/add-userdic.sh") #####error my-dic.csv을 메캅ko안에 
        subprocess.call("ls")

        print("\n<<make install>>")
        subprocess.call(["make", "install", 'DESTDIR=../userlocallibmecab/'])
    
    # usr 권한이 없어 사용 불가능하기 때문에, /home/dapi2/TIBigdataMiddleware/TextMining/userlocallibmecab 을 새로 만들고 사용
    # make install 시에 DESDIR 지정
    mecab = Mecab('/home/dapi2/TIBigdataMiddleware/TextMining/userlocallibmecab/usr/local/lib/mecab/dic/mecab-ko-dic') #/usr/local/lib/mecab/dic/mecab-ko-dic을 자동으로 참조
   
    #success, doc = stop_syn(email, keyword, savedDate, mecab, wordclass)
    success, doc = stop_syn_add_title(email, keyword, savedDate, mecab, wordclass, stopwordTF, synonymTF)

    
    print("전처리 결과: ", doc['content'][0][1700:1900]) #동사, 형용사 --> 추출한 개수가 적기 때문에 출력안됨
    #print("전처리 결과 [0]번째 doc: ", doc[0][1700:1800])
    #print("전처리 결과 [1]번째 doc: ", doc[1][1700:1800])

    #nTokens: 전처리 토큰개수
    nTokens=0
    for i in range(len(doc)):
        for j in range(len(doc['content'][i][""])):
            length = len(doc['content'][i])
        nTokens = length + nTokens
    #print(nTokens)

    if success == True:
    # 사용자사전 test code, true일때만
    # 사용자사전: 신조어일 경우, 띄어쓰기로 분리되어 있는 복합어
        alltokens = [t for tlist in doc for t in tlist]

        for user_word in com_df['단어']:
            if not (user_word in alltokens):
                print(user_word, 'is missing')
        
        # Mongodb 저장
        client=MongoClient(host='localhost',port=27017)
        # print('MongoDB에 연결을 성공했습니다.')
        db=client.textMining

        mdoc={
        "userEmail" : email,
        "keyword" : keyword,
        "savedDate": savedDate,
        "processedDate": datetime.datetime.now(),
        #"duration" : ,
        #"nDocs" : nDocs,
        "nTokens" : nTokens,
        "tokenList" : doc['content'],
        "titleList" : doc['title'],
        "addTitle" : "Yes"
        }
        db.preprocessing.insert(mdoc)

        print('MongoDB에 저장 되었습니다.')

    return success, doc['content'][0][:100] #전체 형태소 분석한 단어들의 목록 (kubic 미리보기에 뜨도록)

#compound_add_text("21800409@handong.edu", "통일", "2021-08-06T11:52:05.706Z", "010", False, False, False)

