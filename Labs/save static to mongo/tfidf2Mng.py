import json
TFIDF_DATA_DIR = "./tfidfTotaldata.json"

with open(TFIDF_DATA_DIR,'r', encoding="utf-8") as fp:
    tfidfData = json.load(fp)

import pymongo
from pymongo import MongoClient
client = MongoClient('localhost',27017)
db = client.analysis0919
collection = db.tfidf
collection.insert_many(tfidfData)