"""
cmm.py
purpose : common features for all algorithm usage

"""

import time
from datetime import datetime

SAMP_DATA_DIR = "./raw data sample/rawData30.json" 

LDA_DIR_FE = "../TIBigdataFE/src/assets/special_first/data.json"

# current date and time
now = datetime.now()
print("Warning! : current version has initialize twice the cmm module...need to be fixed later on...")
start = time.time()

# time taken evaluation
def showTime():
    seconds = time.time() - start
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    # print("투입된 문서의 수 : %d\n설정된 Iteratin 수 : %d\n설전된 토픽의 수 : %d" %(NUM_DOC, NUM_ITER, NUM_TOPICS))
    print("걸린 시간 : %d 시간 : %02d 분 : %02d 초 " % (h, m, s))
