from common import prs
ndoc = 1000
prsResult = prs.readyData(ndoc,True)
import pandas as pd
data = pd.DataFrame(list(prsResult), index = ["id","content","token","contents"]).T
from tensorflow import keras
model = keras.models.load_model('tib_topic_model')

for i in range(data.shape[0]):
    data.loc[i,"token"] = " ".join(data["token"][i])


topicDummy = pd.read_csv('./topicDummy.csv')
data["topic"] = None

import numpy as np
topicList = topicDummy.columns

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
  #pol innt soc cul eco spo
  labels = topicList
  # labels = ['pol', 'eco', 'cul', 'innt', 'spo', 'soc']
  data.loc[i,"topic"] = labels[np.argmax(pred)]


for top in topicList:
  print(data[data["topic"]==top][["token","topic"]].head(3),"\n")
