## phase 0. 디렉토리 추가
## 현재 위치 : \handong\TIBigdataMiddleware\Labs\cosSim>...
## middleware home에도 dir 추가
# from pathlib import Path
# import os
# curDir = os.getcwd()
# curDir = Path(curDir)
# homeDir = curDir.parent.parent
# # comDir = homeDir / "common"

# import sys
# sys.path.append(str(homeDir))





# function : 
def getRcmd(id):
    ## phase 1: 문서 로드 및 전처리
    from common import prs

    data = prs.loadData(30)

    ## 3: 분석
    from sklearn.feature_extraction.text import TfidfVectorizer
    tfidf = TfidfVectorizer()
    tfidf_mtx = tfidf.fit_transform(data["contents"])

    from sklearn.metrics.pairwise import linear_kernel
    cosine_sim = linear_kernel(tfidf_mtx, tfidf_mtx)

    # doc id가 cossinSim 리스트에 몇번째 것인지 파악해야 한다.
    ids = data["id"]
    # for i in ids:
        # print(i)
    index = ids.index(id)

    #recommendation table
    rcmdTbl = list(enumerate(cosine_sim[index]))

    import operator
    tempSort = sorted(rcmdTbl, key=operator.itemgetter(1), reverse=True)
    topFiveRcmd = []
    for i, obj in enumerate(tempSort):
        if i > 5:
            break
        topFiveRcmd.append(obj)

    ids = data["id"]
    rcndList = []
    for oneDoc in topFiveRcmd:
        docIdx = oneDoc[0]#몇번째 문서인지 알려준다.
        # 그 몇번째 문서가... id가 뭔지 찾아야 한다.
        # rcndList.append(ids[docIdx])#id을 담기
        rcndList.append(data["titles"][docIdx])#제목을 담기
        # print(data["titles"][docIdx])



    return { "id" : id, "rcmd" : rcndList }
    """
        angular
            검색 결과 페이지에서 전체 id을 array으로 가지고 있다.
            array id를 플라스크로 보낸다.
        flask
            array id을 받으면
                각 id마다 추천 문서 5개를 뽑는다.
                추천 문서 5개를 제목이 아니라... id으로 보내준다?
                앵귤러가 가지고 있는 것은 ... 그냥 해당 id뿐이다...
                앵귤러에 띄워야 할 정보들 : 추천 문서 제목, 주소.
                추천 문서의 제목과 주소는 플라스크에서 만들어서 보내줘야 한다.
                일단 제목만 받아서 보내는 것을 구현해보자.
                그렇다면 받은 id에 
                { "id" : "abcde", "rcmd" : [ "A", "B", "C", "D", "E" ] , "address" : [ "A", "B", "C", "D", "E" ]}
                
                디버깅을 위해서 띄워야 할 정보 : 그 문서의 내용?
    """


# print(getRcmd("5de1109d582a23c9693cbec9"))