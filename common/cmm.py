"""
cmm.py
purpose : common features for all algorithm usage

"""

import time
from datetime import datetime

# global variables
class DocCorpus:
    NUM_DOC = 0
    titles = []
    contents = []    
    # def __init__ (self):
    #     self.NUM_DOC = 5
    #     self.titles = []
    #     self.contents = []
# ES_INDEX = 'nkdboard'
# ES_INDEX = 'kolofoboard'

# current date and time
now = datetime.now()
start = time.time()
# print("start time : ", now)# 이 모듈을 import할 때 바로 global scope 실행.

# time taken evaluation
def showTime():
    # global start
    seconds = time.time() - start
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    # print("투입된 문서의 수 : %d\n설정된 Iteratin 수 : %d\n설전된 토픽의 수 : %d" %(NUM_DOC, NUM_ITER, NUM_TOPICS))
    print("걸린 시간 : %d 시간 : %02d 분 : %02d 초 " % (h, m, s))
