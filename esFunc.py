from elasticsearch import Elasticsearch

backEndUrl = "http://203.252.103.86:8080"
es = Elasticsearch(backEndUrl)

INDEX = "nkdb"


def esClean(data):
    data = data['hits']['hits']
    # print(data)
    return data

def nkdbFile(SIZE):
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
    results = es.search(index=INDEX, body=doc)
    
    data = esClean(results)
    return data

def nkdbNoFile(SIZE):
    doc = {
        'size': SIZE,
        'query': {
            "exists": {
                "field": "file_extracted_content"
            }
        }
    }
    results = es.search(index=INDEX, body=doc)

    esClean(results)
    return