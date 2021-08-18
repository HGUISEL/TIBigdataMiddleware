import topic_analysis.esAccount as esAcc
from topic_analysis.dataPrePrcs import dataPrePrcs
from topic_analysis.__get_logger import __get_logger
import pandas as pd
import numpy as np
import pickle
import json
import os
import h5py
import csv
from elasticsearch import Elasticsearch
import os.path
import traceback
import sys
import re
import logging

def Pre_date(date):
    try:
        logger.info('Elasticsearch server에 접속을 시도합니다.')
        es = Elasticsearch(
        [esAcc.host],
        http_auth=(esAcc.id, esAcc.password),
        scheme="https",
        port= esAcc.port,
        verify_certs=False
    )
        logger.info('Elasticsearch server에 성공적으로 접속하였습니다.')
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)#+"\n"+ str(trace_back)
        logger.error('Elasticsearch server 접속에 실패하였습니다. %s',message)
        #sys.exit()

    #이전&현재 데이터
    try:
        logger.info('Elasticsearch server에 데이터를 요청합니다.')
        resp=es.search( 
            index= esAcc.index, 
            body={   
                "size":100,
                "query":{
                    "range" :{
                        "timestamp":{
                            #"type":"date",
                            "lte":date,#이전,
                            "format": "yyyy-MM-dd"
                        }
                    },
                },
            },    scroll='1s'
        )
        #old_scroll_id = resp["_scroll_id"]
        sid = resp["_scroll_id"]
        fetched =len(resp['hits']['hits'])
        
        print("fetched: ",fetched)
        #fetched =len(resp['hits']['hits'])

        hash_key=[]
        titles=[]
        contents=[]
        times=[]
        tokenized_doc=[]
        corpus=[]
        corpus2=[]
        count=0

        print('0번부터 99번까지 100개의 데이터를 처리합니다.')
        #f.write('0번부터 99번까지 100개의 데이터를 처리합니다.')
        for i in range(fetched):
            if "file_extracted_content" in resp['hits']['hits'][i]["_source"].keys():    
                hash_key.append((resp['hits']['hits'][i]["_source"]["hash_key"])) 
                titles.append((resp['hits']['hits'][i]["_source"]["post_title"]))
                times.append((resp['hits']['hits'][i]["_source"]["timestamp"]))
                contents.append((resp['hits']['hits'][i]["_source"]["file_extracted_content"]))
    
        from os import path
        resp_count = 0
        while len(resp['hits']['hits']):
            resp_count+=1
            print(resp_count*100,'번부터', resp_count*100+99, '번까지 100개의 데이터를 처리합니다.')
            #f.write(resp_count*100,'번부터', resp_count*100+99, '번까지 100개의 데이터를 처리합니다.')
            resp=es.scroll(scroll_id=sid, scroll='1s')
            fetched=len(resp['hits']['hits'])
            for doc in resp['hits']['hits']:
                if "file_extracted_content" in doc["_source"].keys():
                    hash_key.append((doc["_source"]["hash_key"])) 
                    titles.append((doc["_source"]["post_title"]))
                    times.append((doc["_source"]["timestamp"]))    
                    contents.append(doc["_source"]["file_extracted_content"])
        logger.info("Elasticsearch로부터 데이터를 불러왔습니다.")
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)#+"\n"+ str(trace_back)
        logger.error('Elasticsearch server 데이터를 불러오는데 실패하였습니다. %s',message)
        #sys.exit()
             
    #형태소 분석기
    try:
        logger.info('형태소 분석기를 실행합니다. ')
        tokenized_doc=dataPrePrcs(contents)
        logger.info('형태소 분석기를 실행을 완료하였습니다. ')
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)#+"\n"+ str(trace_back)
        logger.error('형태소 분석기 실행에 실패하였습니다. %s',message)
        #sys.exit()
    return hash_key, titles, tokenized_doc, contents, times
