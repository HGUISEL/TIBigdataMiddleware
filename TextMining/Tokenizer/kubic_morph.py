MECAB_DIR = "/home/middleware/mecab"

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

# from konlpy.tag import Mecab
from jamo import h2j, j2hcj
import re

import account.MongoAccount as monAcc

## Morphological analysis(형태소 분석)
from konlpy.tag import Kkma
import nltk

import logging
import traceback
logger = logging.getLogger("flask.app.morph")


 
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

def is_english(title):
    hangul = re.compile('[ㄱ-ㅣ가-힣]')
    return title == hangul.sub("",title)

def makePosListEN(datas, wordclass, logger, stopword_file):
    posList=[]
    # nltk.download('averaged_perceptron_tagger')

    for j in range(len(datas)):
        sentencePosList = []
        tokenToAnalyze=[]
        poss = nltk.word_tokenize(datas[j])
        poss = nltk.pos_tag(poss)
        # datas['result'] = posList
        # print(poss[:100])

        # 대상토큰 저장 리스트
        targetPosTagLst = []
        # 경우에 따라 대상토큰 추가
        if wordclass[0]=='1': # 동사만
            for tag in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
                targetPosTagLst.append(tag)
        if wordclass[1]=='1': # 명사
            for tag in ["NN", "NNS", "NNP", "NNPS"]:
                targetPosTagLst.append(tag)
        if wordclass[2]=='1': # 형용사 
           for tag in ["JJ", "JJR", "JJS"]:
                targetPosTagLst.append(tag)

        for token, pos in poss:
            if  pos in targetPosTagLst: # 대상 토큰인 경우
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
    return posList

def makePosListKR(mecab, datas, wordclass, logger, stopword_file):
    posList=[]

    for j in range(len(datas)):
        sentencePosList = []
        tokenToAnalyze=[]
        poss = mecab.pos(datas[j])
        # datas['result'] = posList
        # print(poss[:100])

        # 대상토큰 저장 리스트
        targetPosTagLst = []
        # 경우에 따라 대상토큰 추가
        if wordclass[0]=='1': # 동사만
            targetPosTagLst.append("VV")
        if wordclass[1]=='1': # 명사
            for tag in ["NNG", "NNP", "NNB", "NNBC", "NR"]:
                targetPosTagLst.append(tag)
        if wordclass[2]=='1': # 형용사 
            targetPosTagLst.append("VA")

        for token, pos in poss:
            if  pos in targetPosTagLst: # 대상 토큰인 경우
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
    return posList

def makePosList(mecab, datas, wordclass, logger, engIdxList, stopword_file):
    result = []
    for i in range(len(datas['all_content'])):
        if i in engIdxList:
            posList = makePosListEN(datas['all_content'][i], wordclass, logger, stopword_file)
        else:
            posList = makePosListKR(mecab, datas['all_content'][i], wordclass, logger, stopword_file)
        result.append(posList)
    return result

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
        # datas = datas[0:1]
        # print(datas['all_content'][1][200:300])
        
        # 영어title인 index 저장
        engIdxList = []
        for idx in range(len(datas['post_title'])):
            if is_english(datas['post_title'][idx]):
                engIdxList.append(idx)
        
        resultList = makePosList(mecab, datas, wordclass, logger, engIdxList, stopword_file)
        logger.info(identification +"형태소 추출 및 불용어사전 처리를 완료하였습니다.")

    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification + '형태소 추출 오류: '+ str(err))
        return False, "형태소 추출 오류, 세부사항: "+ str(e)
    
    # print('\n유의어, 복합어사전 적용 전: ', resultList[0][20000:20100]) #16 이메일
    # print('\n유의어, 복합어사전 적용 전: ', resultList[0][1700:1900]) ##### 


    #유의어를 json형식으로 받고 dict 이용(split필요x)
    if(synonym_file != False):
        syn_dict = dict(synonym_file)
        syn_temp_dict = dict()

        for key, item in syn_dict.items():
            for word in item:
                syn_temp_dict[word] = key
        print(syn_dict)
        print(syn_temp_dict)
        
        #print("유의어사전\n", syn_df, len(syn_df), len(syn_df.columns), syn_df.columns[0])
        #print("[0,1]", syn_df.iloc[0,1], " [0,2]", syn_df.iloc[0,2], "[1,0]", syn_df.iloc[1,0], " [1,1]", syn_df.iloc[1,1], " [1,2]", syn_df.iloc[1,2])
       
        #result = resultList[0]        
        # print("유의어사전 적용 전:", resultList[0][200:210], len(resultList[0]))
        for doc in resultList: #doc개수
            for sentence_list in doc:
                for k in range(len(sentence_list)): 
                    if sentence_list[k] in syn_temp_dict.keys():
                        # print(k, "번째, ", "**유의어 \"" ,sentence_list[k] , "\"(을)를 찾았습니다. \"", syn_temp_dict[sentence_list[k]], '\"(으)로 변경합니다.')
                        sentence_list[k] = syn_temp_dict[sentence_list[k]]   
        # print("\n유의어사전 적용 후:", resultList[0][200:210], len(resultList[0]))
    else:
        return False, "유용어사전 형식 오류"

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


# dir가 있는지 확인하고 없으면 dir만들어주는 함수.
def create_dir(directory, logger, identification):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            logger.info(identification + "사용자사전 폴더가 이미 있습니다. 생성하지 않습니다.")
        return True, None
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification + "사용자사전 폴더 만들기에 실패했습니다. \n 실패사유:" + str(err))
        return False, identification + "사용자사전 폴더 만들기에 실패했습니다. \n 실패사유:" + str(err)

# 원하는 위치(dir)에 mecab 한국어 사전파일(mecab-ko-dic-2.1.1-20180720.tar.gz)압축해제하여 설치하는 함수
# 이미 있으면 설치하지 않는다. 
import tarfile
def install_mecab(dir, logger, identification):
    FILE_PATH = "/home/middleware/mecab-ko-dic-2.1.1-20180720.tar.gz"
    try:
        if not os.path.exists(dir+"/mecab-ko-dic-2.1.1-20180720"):
            logger.info(identification + "사용자사전 파일을 설치합니다.")
            if os.path.exists(dir) and os.path.isfile(FILE_PATH):
                tar_file = tarfile.open(FILE_PATH)
                tar_file.extractall(path=dir)
                tar_file.close()
                return True, None
            else:
                logger.error(identification + "사용자폴더 혹은 메캅 사용자사전 파일이 없습니다.")
                return False, identification + "사용자폴더 혹은 메캅 사용자사전 파일이 없습니다."
        else:
            logger.info(identification + "사용자사전 파일이 이미 설치되어있어 설치하지 않습니다.")
            return True, None
    except Exception as e:
        err = traceback.format_exc()
        logger.error(identification + "사용자사전 폴더에 초기 사전설치를 실패했습니다. \n 실패사유:" + str(err))
        return False, identification + "사용자사전 폴더에 초기 사전설치를 실패했습니다. \n 실패사유:" + str(err)


def compound_add_text(email, keyword, savedDate, wordclass, stopwordTF, synonymTF, compoundTF):
#def compound(email, keyword, savedDate, wordclass): 

    identification = str(email)+'_'+'preprocessing(compound)'+'_'+str(savedDate)+"// "
    logger.info(identification + '전처리(compound함수)를 시작합니다.')

    logger.info(identification + '전처리를 위한 사용자사전 폴더를 생성합니다.')
    USER_MECAB_DIR = MECAB_DIR+"/"+str(email)
    # USER_MECAB_DIR = MECAB_DIR
    
    result = create_dir(USER_MECAB_DIR, logger, identification)
    if not result[0]:
        return result[0], result[1] 

    logger.info(identification+ '사용자사전 폴더에 기본 사용자사전을 설치합니다.')
    result = install_mecab(USER_MECAB_DIR, logger, identification)
    if not result[0]:
        return result[0], result[1] 

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
        with open(USER_MECAB_DIR+"/mecab-ko-dic-2.1.1-20180720/user-dic/my-dic.csv", 'w', encoding='utf-8') as f: 
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
    
    with cd(USER_MECAB_DIR+"/mecab-ko-dic-2.1.1-20180720"):
        
        #subprocess.call("ls")
        logger.info(identification + "\n<<add-userdic.sh>>")
        subprocess.call("ls")

        subprocess.run('./autogen.sh')
        subprocess.run('./configure')
        subprocess.call("make")

        subprocess.run("./tools/add-userdic.sh")
        subprocess.call("ls")

        subprocess.call(["make", "clean"])

        logger.info(identification + "\n<<make install>>")
        subprocess.call(["make", "install", 'DESTDIR='+USER_MECAB_DIR+'/userlocallibmecab/'])
    
    # usr 권한이 없어 사용 불가능하기 때문에, /home/dapi2/TIBigdataMiddleware/TextMining/userlocallibmecab 을 새로 만들고 사용
    # make install 시에 DESDIR 지정
    mecab = Mecab( dicpath = USER_MECAB_DIR+'/userlocallibmecab/usr/local/lib/mecab/dic/mecab-ko-dic') #/usr/local/lib/mecab/dic/mecab-ko-dic을 자동으로 참조
   
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
    # 전처리 실패했을 시 오류메세지
    else:
        return success, doc

    try:
        return_result_list = make_return_result_list(doc['content'])

    except Exception as e:
        err = traceback.format_exc()
        logger.info(identification + "return list를 만드는 중에 에러 발생 세부사항: " + str(err))
        return False, "결과 리스트 생성 도중 오류가 발생하였습니다. 세부사항: "+ str(e)

    
    # 사용자사전 test code, true일때만
    # 사용자사전: 신조어일 경우, 띄어쓰기로 분리되어 있는 복합어
    alltokens = [t for tlist in doc['content'] for t in tlist ]
    alltokens = [t for tlist in alltokens for t in tlist]
    print("*************",len(alltokens)," ",len(com_df['단어']))
    for user_word in com_df['단어']:
        if not (user_word in alltokens):
            logger.error(user_word + 'is missing')
        # else:
        #     print(user_word+"을(를) 찾았습니다.")
    
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
    db.preprocessing.insert_one(mdoc)

    logger.info(identification + 'MongoDB에 저장 되었습니다.')


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

result, doc = compound_add_text('21800520@handong.ac.kr', '남북통일', "2022-06-29T16:01:37.217Z", "010", False, False, False)


if result:
    print(doc["tokenList"])
else:
    print(doc)