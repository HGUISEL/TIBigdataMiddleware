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
def getRcmd(cosine_sim, index):
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

topF = getRcmd(cosine_sim, 5)

for oneDoc in topF:
    docIdx = oneDoc[0]
    
    print(data["titles"][docIdx])