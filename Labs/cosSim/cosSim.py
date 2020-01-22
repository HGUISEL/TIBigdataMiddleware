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
# data = prs.readyData(30)
# print(data)

data = prs.loadData(30)
# print(type(data))
# data = data["contents"]
# print(data)
## 3: 분석

from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer()
tfidf_mtx = tfidf.fit_transform(data["contents"])

# print(tfidf_mtx.shape)

from sklearn.metrics.pairwise import linear_kernel
cosine_sim = linear_kernel(tfidf_mtx, tfidf_mtx)

# print(type(cosine_sim[0]))