import json

FILE_DIR = "../../raw data sample/rawrawData.json"

with open(FILE_DIR,'r', encoding="utf-8") as fp:
    esData = json.load(fp)

meaningful_data = esData['hits']['hits']

body = ""

for i,d in enumerate(meaningful_data):
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

from elasticsearch import Elasticsearch
import socket
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]



DB_URL = "http://localhost:9200/nkdb"
# DB_URL = get_ip_address()  # '192.168.0.110'
# if(DB_URL != 203.252.103.123):
#   DB_URL = "http://localhost:9200/nkdb"
print(DB_URL)
es = Elasticsearch(DB_URL)
es.bulk(body)