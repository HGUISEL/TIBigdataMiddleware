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
    return esQuary(doc)


def esGetDocs(sizeDoc):
    # app = Flask(__name__)
    # app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

    corpusArr = []

# query whith does not have a filed "file_extracted_content"
    result = nkdbNoFile(sizeDoc)

    for oneDoc in result:
        oneDoc = oneDoc["_source"]
        corpusArr.append((oneDoc["post_title"], oneDoc["post_body"]))

# query whith DOES have a filed "file_extracted_content"
    result = nkdbFile(sizeDoc)

    for oneDoc in result:
        oneDoc = oneDoc["_source"]
        corpusArr.append((oneDoc["post_title"], oneDoc["file_extracted_content"]))


# store data as a file
    with open('rawData.json', 'w', -1, "utf-8") as f:
            json.dump(corpusArr, f, ensure_ascii=False)

    return 