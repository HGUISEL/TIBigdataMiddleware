import json

FILE_DIR = "../../raw data sample/rawrawData.json"

with open(FILE_DIR,'r', encoding="utf-8") as fp:
    esData = json.load(fp)

# print(type(esData))
# print(len(esData))
# print(len(esData[0]))
# print(type(esData[0]))
# print(len(esData['hits']['hits']))
meaningful_data = esData['hits']['hits']

body = ""

for i,d in enumerate(meaningful_data):
    # print(d['_id'])
    body +=         json.dumps({'index' : 
    {
    '_index' : d['_index'],
    '_type' : d['_type'],
    '_id' : d['_id']
    
    }
        },ensure_ascii=False)

    body += '\r\n'
    body +=json.dumps( 
    {
    'post_body' : d["_source"]['post_body'],
     'post_date' : d["_source"]['post_date'],
     'post_title' : d["_source"]['post_title'],
     'post_writer' : d["_source"]['post_writer'],
     'published_institution' : d["_source"]['published_institution'],
     'published_institution_url' : d["_source"]['published_institution_url'],
     'top_category' : d["_source"]["top_category"]
    },ensure_ascii=False)
    
    body += '\r\n'
    if(i == 1):
        print(body)
# print(body)

from elasticsearch import Elasticsearch
DB_URL = "http://localhost:9200/nkdb"
es = Elasticsearch(DB_URL)
es.bulk(body)


# print("meaningful_data[0].keys() : \n", meaningful_data[0]["_source"].keys())
# data = meaningful_data[0]
# print(data)


# for att in esData[0]:
    # print(att)

# url = "localhost:9200/nkdb/_bulk"
"""
{"index": {"_index": "your_index", "_type": "your_type", "_id": "975463711"}}
{"Amount": "480", "Quantity": "2", "Id": "975463711", "Client_Store_sk": "1109"}
{"index": {"_index": "your_index", "_type": "your_type", "_id": "975463943"}}
{"Amount": "2105", "Quantity": "2", "Id": "975463943", "Client_Store_sk": "1109"}

{"index": {"_id": "1234#5678"}}
{"field": "value", "number": 34}
{"index": {"_id": "5555#7896"}}
{"field": "another", "number": 45}
"""