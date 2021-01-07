"""
config.py
purpose : common features for all algorithm usage

"""

import time
from datetime import datetime
INDEX = "nkdb0919"
ES_SERVER_ADDRESS_PORT = "http://localhost:9200"
MONGO_DATABASE = "analysis0919"
ES_SAVE_DIR = "./raw data sample/" 
# LDA_DIR_FE = "./LDAdata.json"



# 데이터 분석 결과 몽고DB에 저장
# data : 몽고에 저장하려는 데이터. 읽으려는 스키마와 동일해야 함
# database : 몽고의 db 이름
# collection : db의 collection이름
def saveToMongo(data, database, collection):
    import pymongo
    from pymongo import MongoClient
    import json
    client = MongoClient('localhost',27017)
    db = client[database]
    collection = db[collection]
    collection.insert_many(json.loads(data))


# 데이터 분석 시간 측정에 사용
# 시작할 때 startTime 호출
# 시간을 알고 싶은 시점에 showTime 사용
# current date and time
now = datetime.now()
start = time.time()

def startTime():
    return time.time()

# time taken evaluation
def showTime(start = start):
    seconds = time.time() - start
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print("걸린 시간 : %d 시간 : %02d 분 : %02d 초 " % (h, m, s))
