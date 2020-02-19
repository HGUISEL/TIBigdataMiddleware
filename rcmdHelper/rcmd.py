## phase 0. 디렉토리 추가
## 현재 위치 : .\TIBigdataMiddleware\cosSim\

## 다른 모듈을 사용하기 위해  TIBigdataMiddleware 추가
## middleware home에도 dir 추가
from pathlib import Path
import os
curDir = os.getcwd()
curDir = Path(curDir)
homeDir = curDir.parent.parent
# # comDir = homeDir / "common"

import sys
sys.path.append(str(homeDir))

## 다른 모듈에 사용 받기 위해 현재 이 디렉토리 추가
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)


# static directory
TFIDF_DIR = "./rcmdHelper/skl_tfidf.json"
DATA_DIR = "./rcmdHelper/data.json"


"""
# fnction : getSimTbl(data)
# purpose : 전달받은 BoW에 대한 코사인 유사도 테이블을 만든다. sk-learn TF-IDF 사용.
# input : BoW list
# output : array
            [
                [문서 1의 단어 TF-IDF 값들],
                [문서 2의 단어 TF-IDF 값들],
                ...
            ]
"""
def getSimTbl(data):

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import linear_kernel
    tfidf = TfidfVectorizer()
    tfidf_mtx = tfidf.fit_transform(data)

    cosine_sim = linear_kernel(tfidf_mtx, tfidf_mtx)

    # save tfidf result
    import json
    with open(TFIDF_DIR, 'w',encoding="utf-8") as fp:
        json.dump(cosine_sim.tolist(), fp,ensure_ascii=False)


    return cosine_sim

    
"""
* **function : getRcmd(idList, calc = False)**
  * purpose : 전달받은 문서들의 관련문서들을 찍어준다.
  * input : 문서 id list<string>. 연관 문서를 얻으려는 문서들 list
  * output : dictionary 
            {
                "id" : "abcde", 
                "rcmd" : [ "A", "B", "C", "D", "E" ], 
                 "address" : [ "A", "B", "C", "D", "E" ]
            }
               
  * NOTICE : 
    * calc = True으로 호출하면 새로 서버에서 문서를 로드해서 tf-idf 데이터를 저장하고, 
                새로운 결과로 프론트엔드에 전달한다.
    * calc = false으로 호출하면 기존에 저장해둔 정보를 사용한다. 아주 빠르게 프론트엔드에 응답해준다. defualt값.
"""
def getRcmd(idList, calc = False):
    # phase 1: TF-IDF을 새로 업데이트하여 출력할 것인지 결정
    if calc == True:
    # phase 1-1: 문서 로드 및 새로 tfidf 테이블을 만든다.
        from common import prs
        data = prs.loadData(700)
        import json
        with open(DATA_DIR, 'w',encoding="utf-8") as fp:
            json.dump(data, fp,ensure_ascii=False)

        cosine_sim = getSimTbl(data["contents"])
        """
            각 tfidf 테이블을 정렬하는 작업
            현재 상태는 문서의 순서대로 각 문서의 연관 문서가 list에 들어가 있다.
            연관문서를 표현하려면 연관순위가 높은 문서들을 표시해야 하므로,
            문서 유사도가 높은 문서들을 앞으로 정렬한다.
        """
        import operator
        
        sort_cos_sim = []
                                                 # for loop에서 type 변환해서 저장하는게 안되는 모양?
        for i,oneDocRec in enumerate(cosine_sim):#for loop안에서 list element 새로 assgin => index으로 접근. 
                                                 #for i, oneDocRec에서 oneDocRec은 local var이다.
            oneDocRec = list(enumerate(oneDocRec))
            sort_cos_sim.append(sorted(oneDocRec, key=lambda x: x[1], reverse=True))

        # using map
        # sort_cos_sim = map(lambda x : sorted(list(enumerate(x)), key=operator.itemgetter(1), reverse=True),cosine_sim)
        # print(sort_cos_sim[0])

        with open(TFIDF_DIR, 'w') as fp:
            json.dump(sort_cos_sim, fp)

    else:
    # phase 1-2: 저장되어 있는 tf-idf 값과 data 정보 불러옴
        import json
        with open(TFIDF_DIR, 'r') as fp:
            cosine_sim = json.load(fp)
        with open(DATA_DIR, 'r',encoding="utf-8") as fp:
            data = json.load(fp)

    # FE에서 요청한 각 문서가 cossinSim 리스트의 몇번째 문서인지 파악해야 한다.
    ids = data["id"]

    rcmdListAll = []
    for id in idList:
        try:
            index = ids.index(id)# FE에서 요청한 각 문서의 index을 파악
        

            #recommendation table
            rcmdTbl = cosine_sim[index]
            
            # print(rcmdTbl)

            # import operator
            # tempSort = sorted(rcmdTbl, key=operator.itemgetter(1), reverse=True)
            # topFiveRcmd = []
            rcmdList = []
            rcmdListId = []
            for i, oneRcmd in enumerate(rcmdTbl):
                # if i == 0:
                    # continue
                # print(i)
                if i > 5:
                    break
                # print(str(i) + "th index fin!")
                # topFiveRcmd.append(oneRcmd)
                # for oneDoc in oneRcmd:
                docIdx = oneRcmd[0]#몇번째 문서인지 알려준다.
                # print(oneRcmd)
                # 그 몇번째 문서가... id가 뭔지 찾아야 한다.
                # rcmdList.append(ids[docIdx])#id을 담기
                rcmdList.append(data["titles"][docIdx])#제목을 담기
                rcmdListId.append(data["id"][docIdx])
                # docIdx = oneRcmd[0]
                # rcmdList.append()

            # rcmdList = []
            # rcmdListId = []
            # for oneDoc in topFiveRcmd:
            #     docIdx = oneDoc[0]#몇번째 문서인지 알려준다.
            #     # 그 몇번째 문서가... id가 뭔지 찾아야 한다.
            #     # rcmdList.append(ids[docIdx])#id을 담기
            #     rcmdList.append(data["titles"][docIdx])#제목을 담기
            #     rcmdListId.append(data["id"][docIdx])

            rcmdListAll.append({"id" : rcmdListId, "rcmd" : rcmdList})
            # rcmdListAll.append({"id" : id, "rcmd" : rcmdList})
            # print(rcmdListAll)
        except:
            print("error at id ", id)
    

    return rcmdListAll



# if __name__ == "__main__":
#     from common import prs

#     data = prs.loadData(700)
#     cosine_sim = getSimTbl(data["contents"])


