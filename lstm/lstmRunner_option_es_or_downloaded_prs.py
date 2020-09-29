#if pre process docs again...
ndoc = 10000

if False:
    from pathlib import Path
    import os
    curDir = os.getcwd()
    curDir = Path(curDir)
    homeDir = curDir.parent
    # # comDir = homeDir / "common"

    import sys
    sys.path.append(str(homeDir))
    from common import prs
    prsResult = prs.readyData(ndoc)
    import pandas as pd
    data = pd.DataFrame(list(prsResult), index = ["docID","docTitle","token"]).T
    for i in range(data.shape[0]):
        data.loc[i,"token"] = " ".join(data["token"][i])



else:
    import json
    with open('../latestPrsResult/latest_prs_result3000.json', 'r') as f:
        data = json.load(f)

    data_ = {"docID" : data["idList"], "docTitle" : data["titles"], "token" : data["tokenized_doc"]}

    import pandas as pd
    df = pd.DataFrame.from_dict(data_)
#import pandas as pd
    #df = pd.DataFrame.from_dict(data_)
    df_token = df.drop(df[df["token"].map(len) < 1].index)
    df_token = df_token.reset_index(drop=True)

    for i in range(len(df_token)):
        df_token.loc[i,"token"] = " ".join(df_token["token"][i])
    data = df_token
    ndoc = len(data)
    print("number of docs : " + str(ndoc))

topicDummy = pd.read_csv('./topicDummy.csv')
data["topic"] = None
topicDummy = topicDummy.drop(topicDummy.columns[0], axis = 1)
print(topicDummy.columns)

import numpy as np
topicList = topicDummy.columns

from tensorflow import keras
model = keras.models.load_model('tib_topic_model')

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

MAX_NB_WORDS = 5000
MAX_SEQUENCE_LENGTH = 500
#tokenizer = Tokenizer(num_words=MAX_NB_WORDS, filters = " ")
import pickle
# loading
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)


for i, cont in enumerate(data["token"]):
  test = []
  test.append(cont)
  seq = tokenizer.texts_to_sequences(test)
  padded = pad_sequences(seq, maxlen = MAX_SEQUENCE_LENGTH)
  pred = model.predict(padded)
#   cul,eco,innt,it,pol,soc,spo
  labels = topicList
  # labels = ['pol', 'eco', 'cul', 'innt', 'spo', 'soc']
  data.loc[i,"topic"] = labels[np.argmax(pred)]


for top in topicList:
  print(data[data["topic"]==top][["token","topic"]].head(3),"\n")

for topic in topicList:
   sumVal =  (data["topic"]==topic).sum()
   print(topic , " count : ", sumVal)

data = data.rename(columns = {"token" : "words"})

data = data.drop(columns = ['words'])


# #-*- coding:utf-8 -*-
# ctgResult = []
# count = 0
# for topic in topicList:
  
#   ctg = data[data["topic" ]== topic]#pandas comprehension
#   # doc = ctg.to_json(orient = "records",force_ascii=False)
#   doc = ctg.to_dict('records')
#   #print(type(doc))
#   catObj = {
#       "topic" : topic,
#       "doc" : doc
#   }
#   # print(catObj)
#   ctgResult.append(catObj)
data = data.to_json(orient="records",force_ascii=False)

# print(data)
import pymongo
from pymongo import MongoClient
import json
client = MongoClient('localhost',27017)
db = client.analysis0919
collection = db.topics
collection.insert_many(json.loads(data))

# import json
# with open("lstm_result_with_"+str(ndoc)+".json", 'w', -1,encoding='utf8') as f:
#     json.dump(data.to_json(orient="records"),f,ensure_ascii=False)
# import pymongo
# from pymongo import MongoClient
# client = MongoClient('localhost',27017)
# db = client.analysisTest620
# collection = db.topics
# collection.insert_many(ctgResult)
