# KUBIC module : prs.py
# purpose : 데이터 전처리 모듈

import traceback
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from config import showTime
from config import ES_SAVE_DIR
import esFunc

# 운영체제에 따라 미캡 모듈이 다르다.
import os
if os.name == "nt":# 윈도우 운영체제
    from eunjeon import Mecab
else:# 현재 리눅스 서버 및 맥은 konlpy으로 미캡 모듈 import
    from konlpy.tag import Mecab

# num_doc = 0

#RANDOM_MODE
# 알고리즘 정확성 확인을 위해서 문서를 불러와서 순서를 섞는다.
RANDOM_MODE = False

#OFFLINE_MODE
# False : use sample data in ./raw data sample, and do not connet to ES.
BACKEND_CONCT = True


# Phase 1 : ES에서 문서 쿼리 및 content와 title 분리 전처리
"""
function : esLoadDocs
purpose : 문서 로드 해준다.
input : 몇개의 문서의 로드?
output : dictionary : 
        {"id" : idList, "titles" : titles, "contents" : contents}

"""
def esLoadDocs(num_doc):
    #if internet connection failed to backend    
    import json
    import sys
    import traceback
    # print(N
    # UM_DOC)
    # global num_doc
    # if num_doc != num_doc:
        # num_doc = num_doc
        # print("num_doc updated to ", num_doc)
    print("데이터 로드 중...")
    try :
        if BACKEND_CONCT == False:
            raise Exception("서버 연결 불가")
        corpus = esFunc.esGetDocs(num_doc)
        print("connection to Backend server succeed!")
        print(len(corpus),"개의 문서를 가져옴")# 문서의 수... 내용 없으면 뺀다...

    except Exception as e:
        # traceback.print_exc()
        print('Error: {}. {}'.format(sys.exc_info()[0],
                sys.exc_info()[1]))


        print("current dir : " ,os.getcwd())
        print("대체 파일 로드 from ",ES_SAVE_DIR)
        with open(ES_SAVE_DIR, "rt", encoding="UTF8") as f:
            corpus = json.load(f)
        
        print("connection to Backend server failed!")
    showTime() 
    realNumDocs = len(corpus) # 전체 사용 가능한 문서 수를 업데이트한다.
    print(num_doc, "개의 문서 중 실제로 사용 가능한 ",realNumDocs, "개의 문서를 가져왔어요.")
 
    


    # 알고리즘 정확성을 확인하기 위해 일부러 문서 순서를 섞는다.
    if RANDOM_MODE == True:
        print("알고리즘 정확도를 확인하기 위해 문서 순서를 섞습니다. 옵션을 끄려면 common/prs.py에서 property 변경")
        import random
        random.shuffle(corpus)

    print("ES 문서에서 문서 id, 문서 제목, 문서 내용으로 추출 중...")

    idList = []
    titles = []
    contents = []
    count = 0#내용 없는 문서 제외하기
    for idx, doc in enumerate(corpus):
        if doc["content"] != "":#내용이 있는 문서만 추출한다
            # 형식을 모두 string으로 바꿔준다. 백엔드 index 결과들 중에서 string이 아닌 것들이 발견 됨.
            idList.append(changeTypeToString(doc["_id"]))
            titles.append(changeTypeToString(doc["post_title"]))
            contents.append(changeTypeToString(doc["content"]))
        else:
            count += 1

    num_doc = len(contents)
    print("num_doc updated to ", num_doc)

    print(count,"개의 문서가 내용이 없음")
    print("문서 추출 결과, 실제 사용할 수 있는 문서의 수 : %d" %(num_doc))

    corpusIdTtlCtt = {"id" : idList, "titles" : titles, "contents" : contents}
    print("문서 추출 완료!")

    #같은 내용 사용할 때 쿼리 안날려도 됨.
    print("추출한 문서를 TIBmiddleware/latestPrsResult/latest_corpus_with_id_witle_contents.json에 저장했어요.")
    with open("../latestPrsResult/latest_corpus_with_id_witle_contents.json", 'w', -1, "utf-8") as f:
        json.dump(corpusIdTtlCtt, f, ensure_ascii=False)

    return corpusIdTtlCtt


"""
    function : changeTypeToString
    purpose : 주어진 데이터를 string으로 변환. esLoadDocs에서 사용
"""
def changeTypeToString(data):
    if isinstance(data, list):
        return data[0]
    else:
        return data
    

# phase 2 형태소 분석기 + 내용 없는 문서 지우기
def dataPrePrcs(corpus_with_id_title_content):
    # 형태소 분석기 instance
    # okt에서 mecab으로 전환. okt 너무 느림...
    # okt = Okt()
    # tokenized_doc = [okt.nouns(contents[cnt]) for cnt in range(len(contents))]
    idList = corpus_with_id_title_content["id"]
    titles = corpus_with_id_title_content["titles"]
    contents = corpus_with_id_title_content["contents"]
    
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
            # titles.pop(i)ss
    for idx in reversed(failIdxList):
        idList.pop(idx)
        titles.pop(idx)
        contents.pop(idx)

    print("형태소 분석 완료!")
    showTime()

    # 한글자 단어들 지우기!
    print("전체 토큰에서 한 글자 토큰 삭제")
    num_doc = len(tokenized_doc)
    for i in range(num_doc):
        tokenized_doc[i] = [word for word in tokenized_doc[i] if len(word) > 1]

    print("데이터 전처리 완료!")
    print("전처리 완료되어 최종적으로 사용 가능한 문서의 수 : %d" %(num_doc))

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
# inCont : true이면 결과 반환할 때 원래 문서 내용까지 함께 반환
"""
def readyData(num_doc, isCont = False):
    idList = []
    titles = []
    contents = []

    # Phase 1 : ES에서 문서 쿼리 및 content와 title 분리 전처리
    
    print("\n\n#####Phase 1-1 : 데이터 로드 실행#####")
    print("Data Loda CURRENT OPTION : ",
          "\nBACKEND CONNECTION OPTION : ", str(BACKEND_CONCT),
          "\nRANDOM ORDER OPTION : ", str(RANDOM_MODE)
         )
    corpus_with_id_title_content = esLoadDocs(num_doc)# load data and update num_doc

    # phase 2 형태소 분석기 + 내용 없는 문서 지우기

    print("\n\n#####Phase 1-2 : 데이터 전처리 실행#####")
    (idList,titles, tokenized_doc, contents) = dataPrePrcs(corpus_with_id_title_content)

    import json
    prs_result = {"idList" : idList, "titles" : titles, "tokenized_doc" : tokenized_doc, "content" : contents}
    with open("../latestPrsResult/latest_pre_prs_result.json", 'w', -1, "utf-8") as f:
        json.dump(prs_result, f, ensure_ascii=False)
    
    print("형태소 분석 시간이 오래걸렸나요? 마지막 형태소 분석 결과를 로컬 static 파일로 저장했어요. middleware/latest_prs_result.json")

    if isCont == False:
        return idList, titles, tokenized_doc
    else:
        return idList, titles, tokenized_doc, contents




if __name__ == "__main__":
#    readyData(100)
    esLoadDocs(10)
