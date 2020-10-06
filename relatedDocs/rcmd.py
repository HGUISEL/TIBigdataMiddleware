## 다른 모듈을 사용하기 위해  TIBigdataMiddleware 추가
## middleware home에도 dir 추가
from pathlib import Path
import os
curDir = os.getcwd()
curDir = Path(curDir)
homeDir = curDir.parent
# # comDir = homeDir / "common"

import sys
sys.path.append(str(homeDir))
# os.chdir(str(homeDir))
# print(str(homeDir))

## 다른 모듈에 사용 받기 위해 현재 이 디렉토리 추가
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)


"""
* **function : create_related_docs(idList, calc_again = False)**
  * purpose : 전달받은 문서들의 관련문서들을 찍어준다.
  * input : 문서 id list<string>. 연관 문서를 얻으려는 문서들 list
  * output : dictionary 
            {
                "id" : "abcde", 
                "rcmd" : [ [doc_number,  "B", "C", "D", "E" ], 
                 #"address" : [ "A", "B", "C", "D", "E" ]#
            }
               
  * NOTICE : 
    * calc_again = True으로 호출하면 새로 서버에서 문서를 로드해서 tf-idf 데이터를 저장하고, 
                새로운 결과로 프론트엔드에 전달한다.
    * calc_again = false으로 호출하면 기존에 저장해둔 정보를 사용한다. 빠르게 프론트엔드에 응답해준다. defualt값.
"""
def create_related_docs():
    from config import showTime
    from config import startTime
    start = startTime()

    # # phase 1: TF-IDF을 새로 업데이트하여 출력할 것인지 결정
    # # phase 1-1: 문서 로드 및 새로 tfidf 테이블을 만든다.
    # 쿼리 기본 데이터 필요
    #Query docs from es then prs, OR, use latest prs
    if False:
        from common import prs
        data = prs.esLoadDocs(ndoc)
    else:
        import json
        with open('../latestPrsResult/latest_corpus_with_id_witle_contents.json', 'r') as f:
            data = json.load(f)
    print("문서 로드 완료!")


    ID_list = data["id"]
    contents = data["contents"]
    # 코사인 유사도 테이블 필요

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import linear_kernel
    tfidf = TfidfVectorizer()
    for i, d in reversed(list(enumerate(contents))):
        # if(i < 10):
        #     print(d)
        if d ==None:
            print(d)
            contents.pop(i)
    tfidf_mtx = tfidf.fit_transform(contents)

    cosine_sim = linear_kernel(tfidf_mtx, tfidf_mtx)


    if len(ID_list) != len(cosine_sim):
        raise Exception("문서의 갯수가 맞지 않아요. len(ID_list) = ",len(ID_list), "len(cosine_sim) = ", len(cosine_sim))


    rcmdTable = []
    for i,rcmdForOneDoc in enumerate(cosine_sim):
        tupleList = []
        for j, rcmdVal in enumerate(rcmdForOneDoc):
            tupleList.append((ID_list[j], rcmdVal))
        tupleList = sorted(tupleList, key=lambda x: x[1], reverse=True)#sort by high similarity value
        # if i < 3:
        #     print(tupleList)
        rcmdTable.append({"docID" : ID_list[i], "rcmd" : tupleList})

    from common.config import saveToMongo
    saveToMongo(rcmdTable,"test","rcmds")
    
    



if __name__ == "__main__":
    related_docs = create_related_docs()
    



