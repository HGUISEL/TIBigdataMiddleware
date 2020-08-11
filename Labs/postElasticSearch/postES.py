import json

FILE_DIR = "../../raw data sample/rawRawData.json"

with open(FILE_DIR,'r', encoding="utf-8") as fp:
    esData = json.load(fp)

meaningful_data = esData['hits']['hits']
indexName = "frontend_test"
body = ""

for i,d in enumerate(meaningful_data):
    body +=         json.dumps({'index' : 
    {
    '_index' : indexName,
    '_type' : indexName,
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

from elasticsearch import Elasticsearch

#function that find current ip address
# import socket
# def get_ip_address():
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s.connect(("8.8.8.8", 80))
#     return s.getsockname()[0]



DB_URL = "http://203.252.112.14:9200/"+indexName
es = Elasticsearch(DB_URL)
es.bulk(body)
