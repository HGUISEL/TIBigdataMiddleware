import json
import os
import pymongo
from pymongo import MongoClient
import account.MongoAccount as monAcc

TFIDF_DATA_DIR = "/home/kubic/TIBigdataMiddleware/rcmdHelper/outputs"

files = os.listdir(TFIDF_DATA_DIR)

for file in files:
    with open(os.path.join(TFIDF_DATA_DIR, file),'r', encoding="utf-8") as fp:
        print("open: " + str(file))
        content = fp.read()
        data = json.loads(content)
        client = MongoClient(monAcc.host, monAcc.port)
        db = client.analysis
        collection = db.rcmds
        collection.insert_many(data)