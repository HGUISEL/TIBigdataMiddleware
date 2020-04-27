import os
from pathlib import Path
curDir = os.getcwd()
curDir = Path(curDir)
homeDir = curDir.parent.parent

import sys
sys.path.append(str(homeDir))

from common import cmm
from common import esFunc
from common import prs

# rawCorpus = esFunc.esGetDocs(30)
data = prs.readyData(5)

import json
with open("tokened_history.json", 'w', -1, "utf-8") as f:
        json.dump(data[2], f, ensure_ascii=False)
# print(len(result[2]))
# tuple(doc id,title?,tokens)
# each element number = num of doc
# print(type(result[2][0]))
# print(len(result[2][0]))

# arr = []

# for tokenized_doc in result[2]:
    # for token in tokenized_doc:

