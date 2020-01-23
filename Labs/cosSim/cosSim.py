## phase 0. 디렉토리 추가
## 현재 위치 : \handong\TIBigdataMiddleware\Labs\cosSim>...
## middleware home에도 dir 추가
from pathlib import Path
import os
curDir = os.getcwd()
curDir = Path(curDir)
homeDir = curDir.parent.parent
# comDir = homeDir / "common"

import sys
sys.path.append(str(homeDir))


## phase 1: 문서 로드 및 전처리
from common import prs

data = prs.loadData(30)

## 3: 분석
from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer()
tfidf_mtx = tfidf.fit_transform(data["contents"])

from sklearn.metrics.pairwise import linear_kernel
cosine_sim = linear_kernel(tfidf_mtx, tfidf_mtx)


# function : 
def getRcmd(cosine_sim, id):

    # doc id가 cossinSim 리스트에 몇번째 것인지 파악해야 한다.
    ids = data["id"]
    for i in ids:
        print(i)
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
    
    return topFiveRcmd

topF = getRcmd(cosine_sim, "5de113b5b53863d63aa55344") # id을 받는다.

ids = data["ids"]
rcndList = []
for oneDoc in topF:
    docIdx = oneDoc[0]#몇번째 문서인지 알려준다.
    # 그 몇번째 문서가... id가 뭔지 찾아야 한다.
    rcndList.append(ids[docIdx])

    print(data["titles"][docIdx])