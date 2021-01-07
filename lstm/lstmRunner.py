def lstm(ndoc, db):
  #if pre process docs again...
  # True : ask ES server and preprocess again, False: load lastest prs result. prs 시간 오래 걸림
  if True:
      from pathlib import Path
      import os
      curDir = os.getcwd()
      curDir = Path(curDir)
      homeDir = curDir.parent

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

      df_token = df.drop(df[df["token"].map(len) < 1].index)
      df_token = df_token.reset_index(drop=True)

      for i in range(len(df_token)):
          df_token.loc[i,"token"] = " ".join(df_token["token"][i])
      data = df_token
      ndoc = len(data)
      print("number of docs : " + str(ndoc))


  # 분류 학습 결과 매핑 더미
  topicDummy = pd.read_csv('./topicDummy.csv')
  data["topic"] = None
  topicDummy = topicDummy.drop(topicDummy.columns[0], axis = 1)
  print(topicDummy.columns)

  import numpy as np
  topicList = topicDummy.columns


  # 케라스 모델 읽기
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

  data = data.to_json(orient="records",force_ascii=False)


  from common.config import saveToMongo
  saveToMongo(data,db,"topics")


if __name__ == "__main__":
  lstm(10, "test")  