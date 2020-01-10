"""
cmm.py
purpose : common features for all algorithm usage

"""

import time
from datetime import datetime

# Sample Raw Data from Backend directory
# if
# currDir = os.getcwd()
# import os
# currDirPath = os.getcwd()
# currDir = os.path.split(currDirPath)[1]
# if currDir != common:
#     os.chdir()
# print("directory!")
# print(os.path.dirname(currDir))
# from pathlib import Path
# print(Path(currDir).parent)
# os.chdir(r'C:\Folder')
# currDir = os.chdir
# print( type(currDir ))
# if()

# print("\n#########directory path adjustment process##########")
# import oslocal
# currDirPath = os.getcwd()
# currDir = os.path.split(currDirPath)[1]
# # parentDirPath = os.path.split(currDirPath)[0]
# # parDir = os.path.split(parentDirPath)[1]
# if currDir != "common":
#     # try:
#     if currDir == "TIBigdataMiddleware":
#         os.chdir(currDirPath+"\\common")
#         print("dir path adjusted!")
#     else:
#         print("dir path error! check file cmm.py")
# # else:
#     # print("nothing woring with dir parh!")
#     # except Exception as e:
# # print("#####dir path procs fin!#####\n")

SAMP_DATA_DIR = "../raw data sample/rawData.json" 
# SAMP_DATA_DIR = '../raw data sample/'

# global variables
# class DocCorpus:
#     NUM_DOC = 0
#     titles = []
#     contents = []
#     idList = []    
    # def __init__ (self):
    #     self.NUM_DOC = 5
    #     self.titles = []
    #     self.contents = []
# ES_INDEX = 'nkdboard'
# ES_INDEX = 'kolofoboard'

# current date and time
now = datetime.now()
print("now is the time : ", now)
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
