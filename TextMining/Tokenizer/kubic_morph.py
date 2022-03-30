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
# from konlpy.tag import Mecab
from jamo import h2j, j2hcj
import re

import account.MongoAccount as monAcc

## Morphological analysis(형태소 분석)
from konlpy.tag import Kkma

import logging
import traceback
logger = logging.getLogger("flask.app.morph")

# 전처리 & 불용어사전적용
def stop_syn(email, keyword, savedDate, mecab, wordclass, stopwordTF, synonymTF):
#def stop_syn(email, keyword, savedDate, mecab, wordclass): 
    datas = search_in_mydoc2(email, keyword, savedDate)
    #print("data2: ", datas)
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
        
        # print("저장된 토큰\n", tokenToAnalyze[0:100])

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
    #print('\n유의어, 복합어사전 적용 전: ', resultList[3][100:500]) ##### 

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

    identification = str(email)+'_'+'preprocessing(compound)'+'_'+str(savedDate)+"// "
    logger.info(identification + '전처리(compound함수)를 시작합니다.')

    file_data = []

    if compoundTF == True:
        try:
            logger.info(identification + '사용자가 등록한 사전을 적용합니다.')
            compound_file = getCompound(email, keyword, savedDate)  #사용자가 등록한 사전 적용

        except Exception as e:
            app.logger.error(identification+ "사용자 사전 적용에 실패했습니다.")
            return
    else:
        logger.info(identification + 'default 사전을 적용합니다.')
        compound_file = getCompound("default","", "")  # 지정해놓은 default 사용자사전 적용
  
    if(compound_file != False):
        com_df = pd.DataFrame(list(compound_file.items()), columns=['단어', '품사'])
        for idx in range(len(com_df)): 
            jongsung_TF = get_jongsung_TF(com_df['단어'][idx]) 
            line = '{},,,,{},*,{},{},*,*,*,*,*\n'.format(com_df['단어'][idx], com_df['품사'][idx], jongsung_TF, com_df['단어'][idx]) 
            file_data.append(line)
    else:
        return False, "복합어사전 형식 오류"
 
    with open("/home/middleware/mecab/mecab-ko-dic-2.1.1-20180720/user-dic/my-dic.csv", 'w', encoding='utf-8') as f: 
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
    mecab = Mecab('/home/middleware/mecab/usr/local/lib/mecab/dic/mecab-ko-dic') #/usr/local/lib/mecab/dic/mecab-ko-dic을 자동으로 참조
   
    #success, doc = stop_syn(email, keyword, savedDate, mecab, wordclass)
    success, doc = stop_syn(email, keyword, savedDate, mecab, wordclass, stopwordTF, synonymTF)

    
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
        client = MongoClient(monAcc.host, monAcc.port)
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
    
# compound('21800520@handong.edu', '북한', "2021-11-26T02:24:06.283Z", '010', False, False, False)[1]

def stop_syn_add_title(email, keyword, savedDate, mecab, wordclass, stopwordTF, synonymTF):
    
    identification = str(email)+'_'+'preprocessing(stop_syn)'+'_'+str(savedDate)+"// "
    logger.info(identification + '전처리(불용어사전 적용하기)를 시작합니다.')
    try:
        logger.info(identification + 'es에서 데이터를 가져옵니다.')
        success, datas = search_in_mydoc_add_title(email, keyword, savedDate)

        if success == 'failed':
            logger.error(identification + 'es에서 데이터 가져오는 것을 실패하였습니다. \n 실패사유:' + datas)
            return False, datas

        nDocs = len(datas)
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification + "es 데이터 형식이 잘못되었습니다. \n 실패사유:" + datas + str(err))
        return False, datas
    
    try:
        if stopwordTF == True:
          stopword_file = getStopword(email, keyword, savedDate)
        else:
          stopword_file = getStopword('default','', '')
        logger.info(identification + 'stopword 적용완료')
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification + "stopword를 적용할 수 없습니다. 세부사항: " + str(err))
        return False, "stopword를 적용할 수 없습니다. 세부사항: " + str(e)

    try:
        if synonymTF == True:
            synonym_file = getSynonym(email, keyword, savedDate)
        else:
            synonym_file = getSynonym('default','', '') 
        logger.info(identification + 'synonym 적용완료')

    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification + 'synonym 적용오류: '+ str(err))
        return False, "synonym을 적용할 수 없습니다. 세부사항: " + str(e)

    # stopword_file = getStopword(email, keyword, savedDate) #사용자가 등록한 불용어
    # synonym_file = getSynonym(email, keyword, savedDate) #사용자가 등록한 유의어
    
    #####err
    '''
    for i in range(len(datas['all_content'])):
        datas.loc[i,'all_content'] = Kkma().sentences(datas['all_content'][i])
    print(datas[:100])
    '''

    try:
        # 형태소추출
        resultList = []   
        #datas = datas[0:1]
        for i in range(len(datas['all_content'])):
            posList=[]
            for j in range(len(datas['all_content'][i])):
                sentencePosList = []
                tokenToAnalyze=[]
                poss = mecab.pos(datas['all_content'][i][j])
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
                    for k in range(len(tokenToAnalyze)):
                        if tokenToAnalyze[k] not in stopword_file:
                            sentencePosList.append(tokenToAnalyze[k]) ############
                else:
                    logger.error(identification +"불용어 처리에서 오류가 발생했습니다.")
                    return False, "불용어사전 형식 오류"   
                    #print("전처리 결과\n", posList[:100])
                posList.append(sentencePosList)
            resultList.append(posList)
        logger.info(identification +"형태소 추출 및 불용어사전 처리를 완료하였습니다.")

    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification + '형태소 추출 오류: '+ str(err))
        return False, "형태소 추출 오류, 세부사항: "+ str(e)
    
    #print('\n유의어, 복합어사전 적용 전: ', resultList[0][20000:20100]) #16 이메일
    print('\n유의어, 복합어사전 적용 전: ', resultList[0][1700:1900]) ##### 

    ''' 3차원 리스트형식으로 바꾸는 과정중. 잠깐 우의어 복합어 사전 적용 정지
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
                            # print(k, "번째, ", "**유의어 \"" ,ri[k] , "\"(을)를 찾았습니다. \"", syn_df.columns[i], '\"(으)로 변경합니다.')
                            ri[k] = syn_df.columns[i]   
        #print("\n유의어사전 적용 후:", resultList[0][200:300], len(resultList[0]))
    else:
        return False, "유용어사전 형식 오류"
    '''
    if len(resultList) == len(datas['post_title']):
        textDict = dict()
        textDict["title"] = datas['post_title']
        textDict['content'] = resultList
    else:
        return False, "누락된 결과가 았습니다. \n  결과 수 :" + str(len(resultList)) + " 제목 수: " + str(len(datas['post_title']))
        
    return True, textDict

def make_return_result_list(docList):
    result = list()
    for doc in docList:
        docToken = []
        for sentence in doc:
            for corpus in sentence:
                docToken.append(corpus)
                if len(docToken) == 10:
                    break
            if len(docToken) == 10:
                    break
        result.append(docToken)
    return result
                
                


def compound_add_text(email, keyword, savedDate, wordclass, stopwordTF, synonymTF, compoundTF):
#def compound(email, keyword, savedDate, wordclass): 

    identification = str(email)+'_'+'preprocessing(compound)'+'_'+str(savedDate)+"// "
    logger.info(identification + '전처리(compound함수)를 시작합니다.')

    file_data = []

    if compoundTF == True:
        try:
            compound_file = getCompound(email, keyword, savedDate)  #사용자가 등록한 사전 적용
            logger.info(identification + '사용자가 등록한 사전을 적용했습니다.')
        except Exception as e:
            err = traceback.format_exc()
            logger.error(identification+ "사용자 사전 적용에 실패했습니다." + str(err))
            return False, str(e)
    else:
        logger.info(identification + 'default 사전을 적용합니다.')
        compound_file = getCompound("default","", "")  # 지정해놓은 default 사용자사전 적용
  
    if(compound_file != False):
        com_df = pd.DataFrame(list(compound_file.items()), columns=['단어', '품사'])
        for idx in range(len(com_df)): 
            jongsung_TF = get_jongsung_TF(com_df['단어'][idx]) 
            line = '{},,,,{},*,{},{},*,*,*,*,*\n'.format(com_df['단어'][idx], com_df['품사'][idx], jongsung_TF, com_df['단어'][idx]) 
            file_data.append(line)
    else:
        return False, "복합어사전 형식 오류"
    
    try:
        with open("/home/middleware/mecab/mecab-ko-dic-2.1.1-20180720/user-dic/my-dic.csv", 'w', encoding='utf-8') as f: 
            for line in file_data: 
                f.write(line)
    except Exception as e:
        err = traceback.format_exc()
        logger.info(identification + "파일 열기 오류 세부사항: " + str(err))
        return False, "파일 열기 오류  세부사항: "+ str(e)

    class cd:
        def __init__(self, newPath):
            self.newPath = os.path.expanduser(newPath)
 
        def __enter__(self):
            self.savedPath = os.getcwd()
            os.chdir(self.newPath)
 
        def __exit__(self, etype, value, traceback):
            os.chdir(self.savedPath)
    
    with cd("/home/middleware/mecab/mecab-ko-dic-2.1.1-20180720"):
        
        #subprocess.call("ls")
        logger.info(identification + "\n<<add-userdic.sh>>")
        subprocess.call("ls")

        # subprocess.run('./autogen.sh')
        # subprocess.call("make")

        subprocess.run("./tools/add-userdic.sh") #####error my-dic.csv을 메캅ko안에 
        subprocess.call("ls")

        logger.info(identification + "\n<<make install>>")
        subprocess.call(["make", "install", 'DESTDIR=../userlocallibmecab/'])
    
    # usr 권한이 없어 사용 불가능하기 때문에, /home/dapi2/TIBigdataMiddleware/TextMining/userlocallibmecab 을 새로 만들고 사용
    # make install 시에 DESDIR 지정
    mecab = Mecab( dicpath = '/home/middleware/mecab/userlocallibmecab/usr/local/lib/mecab/dic/mecab-ko-dic') #/usr/local/lib/mecab/dic/mecab-ko-dic을 자동으로 참조
   
    #success, doc = stop_syn(email, keyword, savedDate, mecab, wordclass)
    success, doc = stop_syn_add_title(email, keyword, savedDate, mecab, wordclass, stopwordTF, synonymTF)

    # print("전처리 결과: ", doc['content'][0][1700:1900]) #동사, 형용사 --> 추출한 개수가 적기 때문에 출력안됨
    #print("전처리 결과 [0]번째 doc: ", doc[0][1700:1800])
    #print("전처리 결과 [1]번째 doc: ", doc[1][1700:1800])
    if success == True:
        #nTokens: 전처리 토큰개수
        nTokens=0
        for i in range(len(doc['content'])):
            for j in range(len(doc['content'][i])):
                length = len(doc['content'][i])
            nTokens = length + nTokens
        #print(nTokens)
    else:
        return success, doc

    try:
        return_result_list = make_return_result_list(doc['content'])

    except Exception as e:
        err = traceback.format_exc()
        logger.info(identification + "return list를 만드는 중에 에러 발생 세부사항: " + str(err))
        return False, "결과 리스트 생성 도중 오류가 발생하였습니다. 세부사항: "+ str(e)

    if success == True:
    # 사용자사전 test code, true일때만
    # 사용자사전: 신조어일 경우, 띄어쓰기로 분리되어 있는 복합어
        alltokens = [t for tlist in doc for t in tlist]

        for user_word in com_df['단어']:
            if not (user_word in alltokens):
                logger.error(user_word + 'is missing')
        
        # Mongodb 저장
        client = MongoClient(monAcc.host, monAcc.port)
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
        "tokenList" : list(doc['content']),
        "titleList" : list(doc['title']),
        "addTitle" : "Yes"
        }
        db.preprocessing.insert(mdoc)

        logger.info(identification + 'MongoDB에 저장 되었습니다.')
    else:
        return success, doc


    return_mdoc={
        "userEmail" : email,
        "keyword" : keyword,
        "savedDate": savedDate,
        "processedDate": str(datetime.datetime.now()),
        "nTokens" : nTokens,
        "tokenList" : return_result_list,
        "titleList" : list(doc['title']),
        "addTitle" : "Yes"
        }
    return success, return_mdoc #전체 형태소 분석한 단어들의 목록 (kubic 미리보기에 뜨도록) --> 출력 형태 변경

result, doc = compound_add_text('21800520@handong.edu', '북한', "2021-09-07T07:01:07.137Z", "010", False, False, False)

print(doc["tokenList"])