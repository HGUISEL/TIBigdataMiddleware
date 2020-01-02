from elasticsearch import Elasticsearch
import json

backEndUrl = "http://203.252.103.86:8080"
es = Elasticsearch(backEndUrl)

INDEX = "nkdb"

"""
function : esQuary(int)
purpose : es에 직접 쿼리를 보내고 간단한 전처리.
    아직 전처리가 끝난 상태는 아니다.
input : 쿼리 body json object
output : 간단한 전처리가 끝난 데이터
"""
def esQuary(doc):
    data = es.search(index=INDEX, body=doc)
    # data = data['hits']['hits'][0]["_source"]
    data = data['hits']['hits']

    return data


"""
function : nkdbFile(int)
purpuse : es에 파일이 없는 문서를 size 개수 만큼 요청
    아직 전처리가 안되어 있는 raw 상태를 반환한다.
input : int : 가지고 오려는 문서의 개수
output : es quary output. 복잡하다... [_source][...]...
"""
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


"""
function : nkdbFile(int)
purpuse : es에 파일이 있는 문서를 size 개수 만큼 요청
    아직 전처리가 안되어 있는 raw 상태를 반환한다.
input : int : 가지고 오려는 문서의 개수
output : es quary output. 복잡하다... [_source][...]...
"""
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
"""
function : esGetDocs(int)
purpose : es에서 문서를 가지고 와서 문서 뭉치를 list으로 반환해준다.
input : int : 가지고 오고 싶은 문서의 개수
output : [
    ("문서 제목", "문서 내용"),
    ("문서 제목2", "문서 내용2"),
    ...
]
"""
def esGetDocs(sizeDoc):

    corpus = []

    ########################################################
    """
    데이터베이스에는 첨부 파일이 있는 문서와 없는 문서가 있다.
    파일 있는 문서와 없는 문서를 모두 가지고 오고 싶으면 both = 1
    
    파일이 있는 문서만 가지고 오고 싶으면 fileY = 1
    파일이 없는 문서만 가지고 오고 싶으면 fileY = 0
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

    """
    파일이 있는 문서와 없는 문서를 모두 가지고 올 때, 
    가지고 오는 전체 문서의 수가 짝수 이면 균등하게 나누고,
    홀수 이면 ( 파일이 없는 문서의 수 + 1 ) = ( 파일이 있는 문서의 수 )
    """
    if both == 1:
        if sizeDoc % 2 == 0:
            sizeDocN = sizeDoc / 2 + 1
            sizeDocY = sizeDoc / 2
        else:
            sizeDocN = sizeDocY = sizeDoc / 2
    else:
        if fileY == 1:
            sizeDocY = sizeDoc
        else:
            sizeDocN = sizeDoc



# 전처리
# 현재 상태 : 문서 뭉치 : [[제목,내용],[제목,내용],...]
# LDA작업은 문서의 내용을 가지고 하므로, 제목과 내용을 분리시켜야 한다.
# 제목을 다루는 array와 내용을 가지는 array을 따로 분리.
# 아랫 단에서 제목과 문서의 빈도 수를 묶을 때 제목을 다시 사용.


# 첨부파일이 없는 문서들
    if fileN == 1:
        result = nkdbNoFile(sizeDocN)
        for oneDoc in result:
            oneDoc = oneDoc["_source"]
            
            if oneDoc["post_body"]:# 내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
                corpus.append( (oneDoc["post_title"], oneDoc["post_body"]) )
                


# 첨부파일이 존재하는 문서들
    if fileY == 1:
        result = nkdbFile(sizeDocY)

        # 전처리 2 for 첨부파일이 있는 데이터
        for oneDoc in result:
            oneDoc = oneDoc["_source"]
            
            if oneDoc["file_extracted_content"]:# 내용이 비어있는 문서는 취하지 않는다. if string ="", retrn false.
                corpus.append( (oneDoc["post_title"], oneDoc["file_extracted_content"]) )
    
    return corpus


"""
function : esGetDocsSave(int)
purpose : es에 connect하여 받은 argument 만큼의 문서를 가지고 온다. 
            그리고 그 문서를 Data folder에 저장.
input : int : 가지고 오려는 문서의 수
output : None
"""
def esGetDocsSave(sizeDoc):
    data = esGetDocs(sizeDoc)
    with open('./Datas/rawData'+str(sizeDoc)+".json", 'w', -1, "utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

"""
function : esGetADoc()
purpose : es에서 random을 선택된 문서를 1개를 가지고 온다. 
input : int : 가지고 오려는 "후보" 문서의 수. default size = 500
output : random하게 선택된 문서 1개의 내용 string type

"""
def esGetADoc(sizeDoc = 500):
    corpus = esGetDocs(sizeDoc)
    num = len(corpus)

    import random
    rd = random.randrange(0,num)
    # print(rd)
    doc = corpus[rd][1]
    # print(doc)
    return doc