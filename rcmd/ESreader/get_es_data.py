"""
ver. 2022-04-01.
Written by yoon-ho choi.
contact: yhchoi@handong.ac.kr
"""
import pandas as pd
from konlpy.tag import Mecab
import re
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import warnings
import sys
import os 
sys.path.append(os.path.abspath('/home/frontend/rcmd/ESreader'))
import esAccount as esAcc

warnings.filterwarnings("ignore")

def get_es_data():
    """
    NOTE:
    - Elastic search version: 7.12.1.
      The latest version of ES API is different from this version.
      Therefore, using the 7.12.1 version is recommended.

    - Initialize elastic search object with authentication information.
      Each information is stored in esAccount.
      "index" means that ES index in the backend server, which contains
      post title, hash_key, contents in the documents, etc.
    """
    es = Elasticsearch(
            [esAcc.host],
            http_auth=(esAcc.id, esAcc.password),
            scheme="https",
            port= esAcc.port,
            verify_certs=False
        )
    index = esAcc.index
    print("Selected index contains ",es.count(index=index), "documents.")
    
    """
    NOTE:
    - Elastic search dsl version: 7.4.0
    - Send ES a query to get document information by using elasticseach_dsl
    """
    s = Search(using=es, index=index)

    """
    NOTE:
    - Build a corpus of collected documents.
    - The information that we need is hash_key, post_title, and post_body/file_extracted_content.
    """
    count = 0
    es_data = []
    for hit in s.scan():
        tmp_dict = hit.to_dict()
        if 'file_extracted_content' in tmp_dict.keys():
            es_data.append({
                    'hashkey': tmp_dict.pop('hash_key'),
                    'post_title': tmp_dict.pop('post_title'),
                    'content': tmp_dict.pop('file_extracted_content')
                    })
        else:
            es_data.append({
                    'hashkey': tmp_dict.pop('hash_key'),
                    'post_title': tmp_dict.pop('post_title'),
                    'content': tmp_dict.pop('post_body')
                    })
        if(len(es_data) > 10000):
            print(count * 10000)
            os.makedirs('./data/',exist_ok=True)
            df = pd.DataFrame(es_data)
            df.to_csv('./data/d_'+str(count)+'.csv')
            es_data.clear()
            count = count + 1
    if(len(es_data) != 0):
        os.makedirs('./data/',exist_ok=True)
        df = pd.DataFrame(es_data)
        df.to_csv('./data/d_'+str(count)+'.csv')
        es_data.clear()
   
    return count

#print(get_es_data())
