import json
TFIDF_DATA_DIR = "../../../TIBigdataFE/src/assets/entire_tfidf/data.json"

with open(TFIDF_DATA_DIR,'r', encoding="utf-8") as fp:
    tfidfData = json.load(fp)

import pymongo
from pymongo import MongoClient
client = MongoClient('localhost',27017)
db = client.user
collection = db.tfidf
collection.insert_many(tfidfData)