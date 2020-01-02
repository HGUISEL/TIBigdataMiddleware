from elasticsearch import Elasticsearch
import json

backEndUrl = "http://203.252.103.86:8080"
es = Elasticsearch(backEndUrl)

INDEX = "nkdb"


def esQuary(doc):
    data = es.search(index=INDEX, body=doc)
    # data = data['hits']['hits'][0]["_source"]
    data = data['hits']['hits']

    return data


def nkdbNoFile(SIZE):
    doc = {
        'size': SIZE,
        'query': {
            # 'match_all' : {}
            # "exists":{
            #     "field" : "file_extracted_content"
            # },
            "bool": {
                "must_not": {
                    "exists": {
                        "field": "file_extracted_content"
                    }

                }
            }
        }
    }

    return esQuary(doc)

def nkdbFile(SIZE):
    doc = {
        'size': SIZE,
        'query': {
            "exists": {
                "field": "file_extracted_content"
            }
        }
    }
    # return esQuary(doc)["file_extracted_content"]
    return esQuary(doc)





# Query to ES New Version 191227
# query whith does not have a filed "file_extracted_content"

def esGetDocs(sizeDoc):

    corpus = []

    ########################################################
    """
    파일이 있는 문서와 없는 문서가 있다.
    둘 다 elasticsearch에서 가지고 오고 싶으면 both = 1
    only Yes 첨부파일 : fileY = 1
    아니면 fileN = 0

    """
    ########################################################

    both = 1
    fileY = 0

    # dont touch this.
    fileN = 1

    if fileY == 1:
        fileN = 0
    else:
        fileN = 1

    if both == 1:
        fileY = 1
        fileN = 1


# 전처리
# 현재 상태 : 문서 뭉치 : [[제목,내용],[제목,내용],...]
# LDA작업은 문서의 내용을 가지고 하므로, 제목과 내용을 분리시켜야 한다.
# 제목을 다루는 array와 내용을 가지는 array을 따로 분리.
# 아랫 단에서 제목과 문서의 빈도 수를 묶을 때 제목을 다시 사용.


# 첨부파일이 없는 문서들
    if fileN == 1:
        result = nkdbNoFile(sizeDoc)
        for oneDoc in result:
            oneDoc = oneDoc["_source"]
            
            if oneDoc["post_body"]:# 내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
                corpus.append( (oneDoc["post_title"], oneDoc["post_body"]) )
                


# 첨부파일이 존재하는 문서들
    if fileY == 1:
        result = nkdbFile(sizeDoc)

        # 전처리 2 for 첨부파일이 있는 데이터
        for oneDoc in result:
            oneDoc = oneDoc["_source"]
            
            if oneDoc["file_extracted_content"]:# 내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
                corpus.append( (oneDoc["post_title"], oneDoc["file_extracted_content"]) )

    # print(corpus)
    
    return corpus


def esGetDocsSave(sizeDoc):
    data = esGetDocs(sizeDoc)
    with open('./Datas/rawData'+str(sizeDoc)+".json", 'w', -1, "utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def esGetADoc(sizeDoc = 500):
    corpus = esGetDocs(sizeDoc)
    num = len(corpus)

    import random
    rd = random.randrange(0,num)
    # print(rd)
    doc = corpus[rd][1]
    # print(doc)
    return doc