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

def update_mongo(count, resetMongo = False):
    client = MongoClient(host=mAcc.host, port=mAcc.port)
    db = client['topic_analysis']
    collection = db['rcmds']

    for i in range(0, count+1):
        data = pd.read_csv('./rcmdFinal/rcmdsFinal_news'+str(i)+'.csv')
        rcmd_data = []

        for i in range(len(data)):
            tmp_rcmd = []
            rcmd_score = data['rcmdDocID,Score'][i]
            rcmd_score = ast.literal_eval(rcmd_score)
            for r_s in rcmd_score:
                tmp_rcmd.append((str(r_s[0]), float(r_s[1])))
            rcmd_data.append({'hashKey':str(data['hashKey'][i]), 'rcmd':tmp_rcmd})
        if resetMongo:
            collection.delete_many({})
        collection.insert_many(rcmd_data)
    return collection.count_documents({})

#update_mongo()
