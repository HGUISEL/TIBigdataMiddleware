from elasticsearch import Elasticsearch
import json
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from config import ES_SAVE_DIR
from config import ES_SERVER_ADDRESS_PORT
es = Elasticsearch(ES_SERVER_ADDRESS_PORT,timeout=30)
from config import INDEX
######################################################################################
"""
* **function : genQuery(boolean, [int])**
  * prpose : es에 보낼 쿼리를 만든다.
  * input : 
    * file 있는 문서인지 없는 문서인지 선택
    * 요청할 size 선택 : [0,infin]
  * output : es 쿼리 body(object)
"""
def genQuery( isFile, size = 0):

    doc = {}
    if size > 0:
        doc['size'] = size

    if isFile == True:
        doc['query'] = {
                "exists": {
                    "field": "file_extracted_content"
                }
        }
    else :
        doc['query'] =  {
            "bool": {
                "must_not": {
                    "exists": {
                        "field": "file_extracted_content"
                    }
                }
            }
        }

    return doc

######################################################################################
"""
* **function : esCount(object)**
  * purpose : 주어진 쿼리 바디에 해당하는 문서의 개수의 카운트를 한다.
  * input : es 쿼리 body
  * output : 문서의 개수(int)
"""
def esCount(doc):
    count = es.count(index=INDEX, body=doc)
    count = count['count']
    return count

######################################################################################
"""
* **function : esQueryRaw(object)**
  * purpose : 전처리를 하지 않은 데이터 반환
  * input : es 쿼리 body object
  * output : json 형태의 데이터(object)
"""
def esQueryRaw(doc):
    data = es.search(index=INDEX, body=doc)
    return data

######################################################################################
"""
* **function : esQuery(object)**
  * purpose : 알고리즘에 맞게 수정할 수 있도록 기본적인 전처리만 끝낸 데이터 반환
  * input : es 쿼리 body object
  * output : json 형태의 데이터(object)
"""
def esQuery(doc):
    data = esQueryRaw(doc)
    data = data['hits']['hits']
    corpus = []
    for oneDoc in data:
        corpus.append( {"_id" :  oneDoc["_id"], "_source" : oneDoc["_source"] }  )

    return corpus






######################################################################################
"""
* **function : nkdbNoFile(int)**
  * purpose : es에 파일이 ***없는*** 문서를 요청한 수 만큼 문서 집단을 반환
  * input : 가지고 오려는 문서의 개수(int)
  * output : (문서 object array)
            [
              {"post_title" : "문서1제목","contents" : "문서1내용"},
              {"post_title" : "문서2제목","contents" : "문서2내용"},
              ...
            ]  
"""
def nkdbNoFile(SIZE):
    print("요청하는 첨부파일 없는 문서의 수 : ", SIZE)
    doc = genQuery(isFile = False, size = SIZE)
    result = esQuery(doc)

    numNoF = len(result)
    print("전달 받은 첨부파일이 없는 문서의 수 : ", numNoF)
    corpus = []

    for oneDoc in result:
        corpus.append(
                        {
                            "_id" : oneDoc["_id"],
                            "post_title" : oneDoc["_source"]["post_title"],
                            "content" : oneDoc["_source"]["post_body"]
                        }
                     )

    return corpus


######################################################################################

"""
* **function : nkdbFile(int)**
  * purpose :es에 파일이 ***있는*** 문서를 요청한 수 만큼 문서 집단을 반환
  * input : 가지고 오려는 문서의 개수(int) 
  * output : (문서 object array)
            [
              {"post_title" : "문서1제목","contents" : "문서1내용"},
              {"post_title" : "문서2제목","contents" : "문서2내용"},
              ...
            ]  
"""
def nkdbFile(SIZE):
    print("요청하는 첨부파일 있는 문서의 수 : ", SIZE)

    doc = genQuery(isFile = True, size = SIZE)
    result = esQuery(doc)    
    numF = len(result)
    print("전달 받은 첨부파일이 있는 문서의 수 : ", numF)

    corpus = []

    for oneDoc in result:
        corpus.append(
                        {
                            "_id" : oneDoc["_id"],
                            "post_title" : oneDoc["_source"]["post_title"],
                            "content" : oneDoc["_source"]["file_extracted_content"]
                        }
                     )
    return corpus





######################################################################################

"""
* **function : esGetDocs(int)**
  * purpose : 첨부 파일이 있든 없든, 종류에 상관 없이 요청한 수 만큼 문서 집단을 반환
  * input : 가지고 오려는 문서의 개수(int)
  * output : (문서 object array)
            [
              {"post_title" : "문서1제목","contents" : "문서1내용"},
              {"post_title" : "문서2제목","contents" : "문서2내용"},
              ...
            ]  
  * NOTICE : 
    * 전체 요청 수를 반으로 나눠서 파일이 있는 문서와 없는 문서에 각각 요청한다. 
    * 첨부 파일이 있는 문서와 없는 문서의 수가 다르기 때문에, 
    * 만약 한쪽에서 수가 모자라면 부족한 부분을 다른 쪽에서 채운다. 
    * 만약 전체 DB에 있는 데이터보다 많은 양을 요청하면 DB에 저장되어 있는 수만 반환.
"""

def esGetDocs(total):
    """
        먼저 file 있는 문서의 개수와 없는 문서의 개수를 카운트

        Y - Y 
        Y - N - Y or N
        N - Y 
        N - N 

        if numReqFileDoc > numFileDoc
            if numReqNFileDoc 
            모자란 수 넘긴다._
        else(안모자라면) pass. 

        if numReqNfileDoc > numNfileDoc
            모자라면 수 넘긴다. 
    
    
        if less:
            if ask other corpus() == true
                return true
            if ask other courpus () == false
                return false

        if enougn 
            if ask other courpus() == true
                return true
            if ask other courpus() == false
                if ask this courpus() == true
                    return true
                if ask this corpus() == false
                    return false

    """
    print("요청받은 문서의 수 : ", total)

    if total == 1:
        return esGetADoc()


    if total % 2 == 0:
            numReqBodyDoc = numReqFileDoc = total / 2
    else:
        numReqBodyDoc = total / 2 + 1
        numReqFileDoc = total / 2
    numReqBodyDoc = int(numReqBodyDoc)
    numReqFileDoc = int(numReqFileDoc)
    print("body : ", numReqBodyDoc)
    print("file : ", numReqFileDoc)


    numFileDoc = esCount(genQuery(isFile = True))
    print("첨부파일이 있는 문서의 전체 수 : ", numFileDoc)
    numBodyDoc = esCount(genQuery(isFile = False))
    print("첨부파일이 없는 문서의 전체 수 : ", numBodyDoc)

    fNum = numFileDoc - numReqFileDoc#모자란 양
    dNum = numBodyDoc - numReqBodyDoc

    if fNum > 0 and dNum > 0:
        pass
    elif fNum > 0 and dNum < 0:
        numReqFileDoc += -dNum#모자란 양을 채워준다
        numReqBodyDoc = numBodyDoc
    elif fNum < 0 and dNum > 0:
        numReqFileDoc = numFileDoc
        numReqBodyDoc += -fNum
    elif fNum <= 0 and dNum <= 0:
        numReqFileDoc = numFileDoc
        numReqBodyDoc = numBodyDoc


    """
    if 여기서 부족하면
        이쪽 문을 닫는다.
        저쪽을 체크.
        저쪽이 가능하면 저쪽으로 넘긴다.
            저쪽에서 해결 가능하면 저쪽에서 담당.
            불가하면 가능한 곳까지 하고 끝.
        저쪽이 안되면 끝.
    여기가 가능하면
        남는 여분 생각해둔다.
        문을 열어둠.
        저쪽을 생각해보면... 
            저쪽이 가능하면 끝.
            저쪽이 불가능하면 이쪽으로 넘겨서 부족분을 담당.
                불가능하면 가능한만큼.
    """

    
    total = numReqFileDoc + numReqBodyDoc # total 가능한 수대로 조정해줘야 함
    
    corpus = []

    data = nkdbFile(numReqFileDoc)
    # print(data)
    for oneDoc in data:
        corpus.append(oneDoc)
    data = nkdbNoFile(numReqBodyDoc)
    for oneDoc in data:
        corpus.append(oneDoc)

    
    
    print("응답 받아 전송한 문서의 수 : ", total)


    return corpus

######################################################################################
"""
* **function : esGetDocsSave([int])**
  * purpose : 첨부 파일이 있든 없든, 종류에 상관 없이 요청한 수 만큼 문서 집단을 반환해서 저장
  * input : [optional : 가지고 오려는 문서의 개수(int)]
  * NOTICE : 
    * default = 20개의 문서를 가지고 옴. 
    * 저장되는 위치는 ./raw data sample/
    * 변수 ES_SAVE_DIR은 config.py에 선언
    * 파일 이름 : rawData.json
    * optional을 선택하면 데이터 파일 이름이 rawDataX.json으로 자동으로 저장
"""
DEFAULT_SAVE = 20
def esGetDocsSave(docSize = DEFAULT_SAVE):
    data = esGetDocs(docSize)
    docSize = len(data)
    if docSize == DEFAULT_SAVE:
        docSize = ""
    with open(ES_SAVE_DIR + 'rawData'+str(docSize)+".json", 'w', -1, "utf-8") as f:
        json.dump(data, f, ensure_ascii=False)






######################################################################################

"""
* **function : esGetADoc([int])**
  * purpose : es에서 random을 선택된 문서를 1개를 가지고 온다.
  * input : [optional : 가지고 오려는 "후보" 문서의 수. default size = 500]
  * output : (문서 object array)
            [
              {"post_title" : "문서 제목","contents" : "문서 내용"}
            ]  
"""
def esGetADoc(docSize=500):
    print("call function : esGetADoc\n%d개의 문서 중 1개를 random으로 선택."%(docSize))
    corpus = esGetDocs(docSize)
    num = len(corpus)

    import random
    rd = random.randrange(0, num)
    print("%d번째 문서를 선택\n" %(rd))
    doc = corpus[rd]
    return doc

if __name__ == "__main__":
    doc = {}
    doc['query'] = {
        "bool":{
            "must":{
                "match" : {
                    "post_title" : "통일정책연구 2004, vol.13, iss.1"
                }
            }
        }
            # "exists": {
            #     "field": "file_extracted_content"
            # }
    }

    data = es.search(index=INDEX, body=doc)
    print(data)
