# KUBIC module : prs.py
# created Data : 어제 :(
# purpose : 데이터 전처리 모듈
import traceback
# from datetime import datetime
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
print("called prs.py")
from cmm import showTime
from cmm import SAMP_DATA_DIR
import esFunc

# 운영체제에 따라 미캡 모듈이 다르다.
import os
if os.name == "nt":# 윈도우 운영체제
    from eunjeon import Mecab
else:# 현재 리눅스 서버 및 맥은 konlpy으로 미캡 모듈 import
    from konlpy.tag import Mecab

NUM_DOC = 0

#RANDOM_MODE
# 알고리즘 정확성 확인을 위해서 문서를 불러와서 순서를 섞는다.
RANDOM_MODE = False

#OFFLINE_MODE
# use sample data in ./raw data sample, and not connet to ES.
# without HGU-WLAN network, use raw data sample no matter this value
BACKEND_CONCT = True


# Phase 1 : ES에서 문서 쿼리 및 content와 title 분리 전처리
"""
function : loadData
purpose : 문서 로드 해준다.
input : 몇개의 문서의 로드?
output : dictionary : 
        {"id" : idList, "titles" : titles, "contents" : contents}

"""
def loadData(num_doc = NUM_DOC):
    #if internet connection failed to backend    
    import json
    import sys
    import traceback
    # print(N
    # UM_DOC)
    global NUM_DOC
    if NUM_DOC != num_doc:
        NUM_DOC = num_doc
        print("NUM_DOC updated to ", NUM_DOC)
    print("데이터 로드 중...")
    try :
        if BACKEND_CONCT == False:
            raise Exception("서버 연결 불가")
        corpus = esFunc.esGetDocs(NUM_DOC)
        print("connection to Backend server succeed!")
        print(len(corpus),"개의 문서를 가져옴")# 문서의 수... 내용 없으면 뺀다...

    except Exception as e:
        # traceback.print_exc()
        print('Error: {}. {}'.format(sys.exc_info()[0],
                sys.exc_info()[1]))


        print("current dir : " ,os.getcwd())
        print("대체 파일 로드 from ",SAMP_DATA_DIR)
        # print("\n\nDEBUG : 현재 실행 directory 위치",os.getcwd(),"\n\n")
        with open(SAMP_DATA_DIR, "rt", encoding="UTF8") as f:
            corpus = json.load(f)
        
        print("connection to Backend server failed!")
    showTime() 
    NUM_DOC = len(corpus) # 전체 사용 가능한 문서 수를 업데이트한다.
    print("NUM_DOC updated to ", NUM_DOC)
 
    print("문서 로드 완료!")
    print()


    # 알고리즘 정확성을 확인하기 위해 일부러 문서 순서를 섞는다.
    if RANDOM_MODE == True:
        import random
        random.shuffle(corpus)


    idList = []
    titles = []
    contents = []
    count = 0
    for idx, doc in enumerate(corpus):
        # print(doc["content"])
        if doc["content"] != "":
            # 형식을 모두 string으로 바꿔준다. 백엔드 index 결과들 중에서 string이 아닌 것들이 발견 됨.
            idList.append(changeTypeToString(doc["_id"]))
            titles.append(changeTypeToString(doc["post_title"]))
            contents.append(changeTypeToString(doc["content"]))
        else:
            count += 1

    NUM_DOC = len(contents)
    print("NUM_DOC updated to ", NUM_DOC)

    print(count,"개의 문서가 내용이 없음")
    print("투입된 문서의 수 : %d" %(NUM_DOC))

    corpusIdTtlCtt = {"id" : idList, "titles" : titles, "contents" : contents}


    with open("../latestPrsResult/latest_corpus_with_id_witle_contents.json", 'w', -1, "utf-8") as f:
        json.dump(corpusIdTtlCtt, f, ensure_ascii=False)

    return corpusIdTtlCtt

def changeTypeToString(data):
    
    if isinstance(data, list):
        return data[0]
    else:
        return data
    

# phase 2 형태소 분석기 + 내용 없는 문서 지우기
def dataPrePrcs(corpus_with_id_title_content):
    # 형태소 분석기 instance
    # okt = Okt()
    # tokenized_doc = [okt.nouns(contents[cnt]) for cnt in range(len(contents))]
    idList = corpus_with_id_title_content["id"]
    titles = corpus_with_id_title_content["titles"]
    contents = corpus_with_id_title_content["contents"]
    #mecab test
    import re
    rex1 = re.compile('[^가-힣0-9*.?,!]')#한글 숫자 자주 쓰는 문자만 취급
    
    tagger = Mecab()
    print("데이터 전처리 중... It may takes few hours...")
    print("regular expression 처리 중...")
    for i,c in enumerate(contents):
        try:
            c = rex1.sub(" ",c)
        except Exception:
            print("에러 : title : ", titles[i], ", content : ", c)# 문서 내용이 None
        # if(i < 10):
        #     print("regex test : ",c)
    print("\n\nmecab 형태소 분석 중...")
    tokenized_doc = []
    failIdxList = []
    for i, c in enumerate(contents):
        try:
            t = tagger.nouns(c)
            # print(t)
            tokenized_doc.append(t)
        except:
            print("에러 : title : ", titles[i], ", content : ", c)
            failIdxList.append(i)
            # 모아뒀다가 나중에 한꺼번에 지워야...
            # contents.pop(i)
            # idList.pop(i)
            # titles.pop(i)
    for idx in reversed(failIdxList):
        idList.pop(idx)
        titles.pop(idx)
    print("형태소 분석 완료!")
    print("투입된 문서의 수 : %d" %(NUM_DOC))
    showTime()

    # 한글자 단어들 지우기!
    num_doc = len(tokenized_doc)
    for i in range(num_doc):
        tokenized_doc[i] = [word for word in tokenized_doc[i] if len(word) > 1]

    print("데이터 전처리 완료!")
    return idList, titles, tokenized_doc, contents


"""
# functin : readData(int)
# purpose : 데이터를 로드해서 형태소 분석 전처리까지 하고 데이터 반환
# input : int : num_doc : 준비할 데이터의 수
# output : [
                ["문서1 단어1", "문서1 단어 2"],
                ["문서1 단어1", "문서1 단어 2"],
                ...
           ]
"""
def readyData(num_doc, isCont = False):
    # NUM_DOC initialize
    global NUM_DOC
    NUM_DOC = num_doc
    idList = []
    titles = []
    contents = []

    # print("in readyData after if, ", NUM_DOC)

    # Phase 1 : ES에서 문서 쿼리 및 content와 title 분리 전처리
    
    print("\n\n#####Phase 1-1 : 데이터 로드 실행#####")
    print("Data Loda CURRENT OPTION : ",
          "\nBACKEND CONNECTION OPTION : ", str(BACKEND_CONCT),
          "\nRANDOM ORDER OPTION : ", str(RANDOM_MODE)
         )
    corpus_with_id_title_content = loadData(NUM_DOC)# load data and update NUM_DOC
    # print(corpus_with_id_title_content)
    # idList = corpus_with_id_title_content["id"]
    # titles = corpus_with_id_title_content["titles"]
    # contents = corpus_with_id_title_content["contents"]
    # phase 2 형태소 분석기 + 내용 없는 문서 지우기
    print("len(content) : ", len(contents))

    print("\n\n#####Phase 1-2 : 데이터 전처리 실행#####")
    (idList,titles, tokenized_doc, contents) = dataPrePrcs(corpus_with_id_title_content)

    import json
    prs_result = {"idList" : idList, "titles" : titles, "tokenized_doc" : tokenized_doc, "content" : contents}
    with open("../latestPrsResult/latest_pre_prs_result.json", 'w', -1, "utf-8") as f:
        json.dump(prs_result, f, ensure_ascii=False)
    
    print("형태소 분석 시간이 오래걸렸나요? 마지막 형태소 분석 결과를 로컬 static 파일로 저장해두었습니다. ./latest_prs_result.json")

    if isCont == False:
        return idList, titles, tokenized_doc
    else:
        return idList, titles, tokenized_doc, contents




if __name__ == "__main__":
#    readyData(10000)
    loadData(10000)
