import os
import sys
import random
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

es = Elasticsearch(['localhost:9200'])
# print(str(es)+"~~")
s = Search(using=es, index="nkdb200803")
# print(str(s)+"~~")
# print(s)
ids = [h.meta.id for h in s.scan()]
print(ids)

date_list = ['2020-01-01', '2020-02-01', '2020-03-01', '2020-04-01', '2020-05-01', '2020-06-01', '2020-07-01', '2020-08-01', '2020-09-01', '2020-10-01', '2020-11-01', '2020-12-01']

for index in range(len(ids)):
    i = random.randrange(0,12)
    os.system('curl -X POST localhost:9200/nkdb200803/_update/' +ids[index]+ '?pretty -H "Content-Type: application/json" -d \'{"doc":{ "indexed_datetime":'+date_list[i].replace('-', '')+'}}\'')