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



## 3: 분석