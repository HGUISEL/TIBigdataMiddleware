"""
ver. 2022-04-01.
Written by yoon-ho choi.
contact: yhchoi@handong.ac.kr
"""
from bson.objectid import ObjectId
from pymongo import MongoClient
import pandas as pd
import json
import MongoAccount as mAcc
import sys
import ast

def update_mongo():
    client = MongoClient(host=mAcc.host, port=mAcc.port)
    db = client['analysis']
    collection = db['rcmds']
    data = pd.read_csv('../cosine_similarity/rcmdsFinal.csv')
    rcmd_data = []

    for i in range(len(data)):
        tmp_rcmd = []
        rcmd_score = data['rcmdDocID,Score'][i]
        rcmd_score = ast.literal_eval(rcmd_score)
        for r_s in rcmd_score:
            tmp_rcmd.append((str(r_s[0]), float(r_s[1])))
        rcmd_data.append({'docID':str(data['docID'][i]), 'rcmd':tmp_rcmd})

    collection.delete_many({})
    collection.insert_many(rcmd_data)
    return collection.count_documents({})

#update_mongo()
