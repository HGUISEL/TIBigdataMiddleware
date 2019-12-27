from elasticsearch import Elasticsearch

backEndUrl = "http://203.252.103.86:8080"
es = Elasticsearch(backEndUrl)

INDEX = "nkdb"


def esClean(doc):
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

    return esClean(doc)


# Query to ES New Version 191227
# query whith does not have a filed "file_extracted_content"
def nkdbFile(SIZE):
    doc = {
        'size': SIZE,
        'query': {
            "exists": {
                "field": "file_extracted_content"
            }
        }
    }
    # return esClean(doc)["file_extracted_content"]
    return esClean(doc)
