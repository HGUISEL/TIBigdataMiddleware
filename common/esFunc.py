from elasticsearch import Elasticsearch
import json
import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from cmm import SAMP_DATA_DIR

backEndUrl = "http://203.252.103.86:8080"
es = Elasticsearch(backEndUrl)

INDEX = "nkdb"
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
    # data = data['hits']['hits'][0]["_source"]
    data = data['hits']['hits']
    # numDoc = len(data)
    # if isFile == True:
    #     print("전달 받은 첨부 파일이 있는 문서의 수 : ", numDoc)
    # else:
    #     print("전달 받은 첨부 파일이 없는 문서의 수 : ", numDoc)
    corpus = []
    for oneDoc in data:
        # oneDoc = oneDoc["_source"] # not work...
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
    doc = genQuery(isFile = False, size = SIZE)
    result = esQuery(doc)

    numNoF = len(result)
    print("전달 받은 첨부파일이 없는 문서의 수 : ", numNoF)
    corpus = []

    for oneDoc in result:
    # if oneDoc["post_body"]:# 내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
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
    doc = genQuery(isFile = True, size = SIZE)
    result = esQuery(doc)    
    numF = len(result)
    print("전달 받은 첨부파일이 있는 문서의 수 : ", numF)

    corpus = []

    for oneDoc in result:
        # if oneDoc["file_extracted_content"]:# 내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
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
            numReqNfDoc = numReqFileDoc = total / 2
    else:
        numReqNfDoc = total / 2 + 1
        numReqFileDoc = total / 2
    numReqNfDoc = int(numReqNfDoc)
    numReqFileDoc = int(numReqFileDoc)

    # numReqFileDoc 
    # numReqNfDoc 
    numFileDoc = esCount(genQuery(isFile = True))
    numNfDoc = esCount(genQuery(isFile = False))

    if numReqFileDoc > numFileDoc: #less (N)
            if numReqNfDoc <= numNfDoc: #cover (N - Y)
                numReqNfDoc += numReqFileDoc - numFileDoc # 가능한 문서 집단으로 부족분 넘긴다.
                numReqFileDoc = numFileDoc # 부족한 문서 집단 요청 수 조정
            else: # less (N - N)
                total = numNfDoc + numFileDoc # total 가능한 수대로 조정해줘야 함
                numReqFileDoc = numFileDoc # 두 문서 집단 모두 요청 수 조정 필요
                numReqNfDoc = numNfDoc
    else:   # elif numReqFileDoc <= numFileDoc # cover (Y) 
        if numReqNfDoc <= numNfDoc: # cover(Y - Y)
            total = total # 그대로. 없애도 되는 if 문
        else: # less (Y - N)
            numReqFileDoc += numReqNfDoc - numNfDoc
            numReqNfDoc = numNfDoc
            # if numReqFileDoc <= numFileDoc: # cover (Y - N - Y)
                # return tru
                # pass 가만히 있으면 된다.
            if numReqFileDoc > numFileDoc: # cover (Y - N - Y)
            # else:#(Y - N - N) less
                # return false
                # less이니까 최대한으로 가져간다.
                numReqFileDoc = numFileDoc
    total = numNfDoc + numFileDoc # total 가능한 수대로 조정해줘야 함
    
    corpus = []

    data = nkdbFile(numReqFileDoc)
    # print(data)
    for oneDoc in data:
        # if oneDoc["file_extracted_content"]:# 내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
        # corpus.append((oneDoc["post_title"], oneDoc["file_extracted_content"]))
        corpus.append(oneDoc)
    data = nkdbNoFile(numReqNfDoc)
    for oneDoc in data:
        # if oneDoc["post_body"]:# 내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
        # corpus.append((oneDoc["post_title"], oneDoc["post_body"]))
        corpus.append(oneDoc)

    
    
    print("응답 받아 전송한 문서의 수 : ", total)


    return corpus

######################################################################################
"""
개발 중... esGetDocs을 더 나은 알고리즘으로...
"""
def esTestMin():
    """
        fileDoc 과 NfileDoc의 수를 먼저 구한다.

        수가 더 적은 min doc 집단을 구한다.

        반으로 나눠서 N -1 혹은 N으로 만든다.

        N 혹은 N-1을 min doc의 수와 비교한다.
            경우 : 두 doc 의 수가 같다.
                
            경우 : 다르다. min doc이 명시적으로 있다.
                min doc에게 N 혹은 N-1을 비교한다.
                if min doc < N
                    남은 수를 max doc에 요청한다.
                

        recursion 함수 만들기

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

        if enough
            return true
        else
            return false

    """





"""
DEPRECIATED
function : esGetDocs(int)
purpose : es에서 문서를 가지고 와서 문서 뭉치를 list으로 반환해준다.
input : int : 가지고 오고 싶은 문서의 개수

output : (문서 dictionary array, 요청에 성공한 문서 수)
문서 dictionary array: [
                            ("문서 제목", "문서 내용"),
                            ("문서 제목2", "문서 내용2"),
                            ...
                        ]
"""
def esGetDocsV1(totalSize):

    corpus = []

    # ########################################################
    # """
    # 데이터베이스에는 첨부 파일이 있는 문서와 없는 문서가 있다.
    # 파일 있는 문서와 없는 문서를 모두 가지고 오고 싶으면 isBoth = 1
    
    # 파일이 있는 문서만 가지고 오고 싶으면 fileY = 1
    # 파일이 없는 문서만 가지고 오고 싶으면 fileY = 0
    # """
    # ########################################################

    # if isFile = True:
        

    # if isBoth == True:
        
    # isBoth = 0
    # fileY = 1

    # # dont touch this.
    # fileN = 1

    # if fileY == 1:
    #     fileN = 0
    # else:
    #     fileN = 1

    # if isBoth == 1:
    #     fileY = 1
    #     fileN = 1

    # print("전체 요청된 문서의 수 : ", totalSize)

    # """
    # 파일이 있는 문서와 없는 문서를 모두 가지고 올 때, 
    # 가지고 오는 전체 문서의 수가 짝수 이면 균등하게 나누고,
    # 홀수 이면 ( 파일이 없는 문서의 수 + 1 ) = ( 파일이 있는 문서의 수 )
    # """

    # if isBoth == True:
    #     if totalSize % 2 == 0:
    #         docSize = hasFileDocSize = totalSize / 2
    #     else:
    #         docSize = totalSize / 2 + 1
    #         hasFileDocSize = totalSize / 2
    #     docSize = int(docSize)
    #     hasFileDocSize = int(hasFileDocSize)
    #     # print("첨부 파일이 있는 문서 요청 수 : ", hasFileDocSize)
    #     # print("첨부 파일이 없는 문서 요청 수 : ", docSize)
    # else:
    #     if fileY == 1:
    #         hasFileDocSize = totalSize
    #         # print("첨부 파일이 있는 문서 요청 수 : ", hasFileDocSize)

    #     else:
    #         docSize = totalSize
    #         # print("첨부 파일이 없는 문서 요청 수 : ", docSize)

    # numHasFileDoc = esCount(isFile = True)
    # numDoc = esCount(isFile = False)

    # if numHasFileDoc > numDoc:
    #     if docSize > numDoc:
    #         hasFileDocSize += docSize - numDoc
    #         docSize = numDoc
    # else:
    #     if hasFileDocSize > numHasFileDoc:
    #         docSize += hasFileDocSize - numHasFileDoc
    #         hasFileDocSize = numHasFileDoc


    """
    purpose:
        전체 요청한 문서 수에서 파일이 있는 문서와 없는 문서로 나눠서 백엔드에 문서 요청

    variables :
        totalSize : 요청한 전체 문서 수
        docSize : 첨부 파일이 없는 일반 문서의 수
        hasFileDocSize : 첨부 파일 있는 문서의 수
    """

    if totalSize % 2 == 0:
            docSize = hasFileDocSize = totalSize / 2
    else:
        docSize = totalSize / 2 + 1
        hasFileDocSize = totalSize / 2
    docSize = int(docSize)
    hasFileDocSize = int(hasFileDocSize)
        # print("첨부 파일이 있는 문서 요청 수 : ", hasFileDocSize)
        # print("첨부 파일이 없는 문서 요청 수 : ", docSize)
    

    # 첨부파일 있는 문서
    doc = genQuery(isFile = True)
    numFileDocSize = esCount(doc)

    if hasFileDocSize > numHasFileDoc:
        docSize += hasFileDocSize - numHasFileDoc
        # hasFileDocSize = numHasFileDoc
    data = nkdbFile(numHasFileDoc)
    
    # if numHasFileDoc != len(data):
    #     # print("ERROR: Num Mismatch")
    #     raise Exception("Num Mismatch in File Doc")

    for oneDoc in data:
        # if oneDoc["post_body"]:# 내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
        corpus.append((oneDoc["post_title"], oneDoc["post_body"]))



    # 첨부 파일 없는 문서
    # doc = genQuery(isFile = False)
    # numDoc = esCount(doc)

    # if docSize > numDoc:
    data = nkdbNoFile(docSize)
    numDoc = len(data)

    # if docSize <  numDoc:
    #     # print("ERROR: Num Mismatch")
    #     raise Exception("Num Mismatch in non-File Doc")

    if docSize > numDoc:
        newTotalSize = numHasFileDoc + numDoc
        print("요청한 문서 수(%d)가 DB에 충분히 없음. 응답 받은 문서 수 : %d" %(totalSize,newTotalSize))
        totalSize = newTotalSize
    else:
        print("요청한 문서 수(%d)를 성공적으로 응답" %totalSize)
    


    if docSize > numDoc:
        hasFileDocSize += docSize - numDoc
        docSize = numDoc

    
    if numHasFileDoc > numDoc:
            docSize = numDoc
    else:
        if hasFileDocSize > numHasFileDoc:
            docSize += hasFileDocSize - numHasFileDoc
            hasFileDocSize = numHasFileDoc

    availSize = numHasFileDoc + numDoc
    if  availSize < totalSize:
        totalSize = availSize






    # genQuery


    
    # if 요청한 문서 수 > 실제 문서 수
    if hasFileDocSize > numHasFileDoc:
        docSize = hasFileDocSize - numHasFileDoc

    data = nkdbNoFile(docSize)
    numDoc = len(data)
    for oneDoc in data:
        # if oneDoc["file_extracted_content"]:# 내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
        corpus.append((oneDoc["post_title"], oneDoc["file_extracted_content"]))

    if docSize > numDoc:
        newTotalSize = numHasFileDoc + numDoc
        print("요청한 문서 수(%d)가 DB에 충분히 없음. 응답 받은 문서 수 : %d" %(totalSize,newTotalSize))
        totalSize = newTotalSize
    else:
        print("요청한 문서 수(%d)를 성공적으로 응답" %totalSize)
    # # 나눈 수가 전체 각각의 문서의 크기에 맞는지 확인
    # """
    # 이유 : 전체 문서 요청 100개를 나눠서 50, 50.
    # 만약 첨부 파일 있는 문서의 수가 50보다 작으면, 
    # 부족한 수 만큼 첨부 파일 없는 문서에서 더 가지고 와야
    # 요청한 문서의 수 맞출 수 있다.
    # """
    # doc = genQuery(isFile = True) #파일 있는 문서 쿼리 바디 생성
    # numHasFileDoc = esCount(doc)# 파일 있는 문서의 수 


    # doc = genQuery(isFile = False) # 파일 없는 문서 쿼리 바디 생성
    # numDoc = esCount(doc) # 파일 없는 문서의 수

    # # DB에 있는 문서들 중
    # # 더 적은 종류(파일이 있는 문서, 없는 문서)의 수를 요청한 수와 비교해야
    # # 요청한 수가 더 적은 문서가 
    # if numHasFileDoc > numDoc:
    #     if docSize > numDoc:
    #         hasFileDocSize += docSize - numDoc
    #         docSize = numDoc
    # else:
    #     if hasFileDocSize > numHasFileDoc:
    #         docSize += hasFileDocSize - numHasFileDoc
    #         hasFileDocSize = numHasFileDoc

    # availSize = numHasFileDoc + numDoc
    # if  availSize < totalSize:
    #     totalSize = availSize

    # 전처리
    # 현재 상태 : 문서 뭉치 : [[제목,내용],[제목,내용],...]
    # LDA작업은 문서의 내용을 가지고 하므로, 제목과 내용을 분리시켜야 한다.
    # 제목을 다루는 array와 내용을 가지는 array을 따로 분리.
    # 아랫 단에서 제목과 문서의 빈도 수를 묶을 때 제목을 다시 사용.
    # data = esQuery(isFile = True, hasFileDocSize)


    # data = esQuery(False, docSize)
   

    return corpus, totalSize

######################################################################################
"""
* **function : esGetDocsSave([int])**
  * purpose : 첨부 파일이 있든 없든, 종류에 상관 없이 요청한 수 만큼 문서 집단을 반환해서 저장
  * input : [optional : 가지고 오려는 문서의 개수(int)]
  * NOTICE : 
    * default = 20개의 문서를 가지고 옴. 
    * 저장되는 위치는 ./raw data sample/
    * 파일 이름 : rawData.json
    * optional을 선택하면 데이터 파일 이름이 rawDataX.json으로 자동으로 저장
"""
DEFAULT_SAVE = 20
def esGetDocsSave(docSize = DEFAULT_SAVE):
    data = esGetDocs(docSize)
    if docSize == DEFAULT_SAVE:
        docSize = ""
    with open(SAMP_DATA_DIR + 'rawData'+str(docSize)+".json", 'w', -1, "utf-8") as f:
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
    # print(rd)
    doc = corpus[rd]
    # print(doc)
    return doc
