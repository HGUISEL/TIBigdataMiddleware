import json
import os
import pymongo
from pymongo import MongoClient

TFIDF_DATA_DIR = "/home/kubic/TIBigdataMiddleware/rcmdHelper/outputs"

files = os.listdir(TFIDF_DATA_DIR)

for file in files:
    with open(os.path.join(TFIDF_DATA_DIR, file),'r', encoding="utf-8") as fp:
        print("open: " + str(file))
        content = fp.read()
        data = json.loads(content)
        client = MongoClient('localhost',27017)
        db = client.analysis
        collection = db.rcmds
        collection.insert_many(data)