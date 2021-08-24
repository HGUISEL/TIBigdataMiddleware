from elasticsearch import Elasticsearch

import TextMining.Tokenizer.esAccount as esAcc 
from TextMining.Tokenizer.kubic_mystorage import *#
#from TextMining.Tokenizer.kubic_mystorage import getMyDocByEmail2

#python app.py하면 문제,,
# import esAccount as esAcc
# from kubic_mystorage import *

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname('TextMining/Tokenizer'))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname('TextMining/Analyzer'))))
from ssl import create_default_context
import re
import pandas as pd

es = Elasticsearch(
        [esAcc.host],
        http_auth=(esAcc.id, esAcc.password),
        scheme="https",
        port= esAcc.port,
        verify_certs=False
)
index = esAcc.index

## Collect data from es(post_date, post_body, file_content) and return dataframe
def search_in_mydoc2(email, keyword, savedDate):
    df = pd.DataFrame()
    #savedDate = datetime.datetime.strptime(savedDate, "%Y-%m-%dT%H:%M:%S.%fZ")
    idList = getMyDocByEmail2(email, keyword, savedDate)
    print('idList=', idList)

    df['idList'] = idList

    dateList=[]
    bodyList=[]
    fileList=[]    
    titleList=[]

    response=es.search( 
        index=index, 
        body={
            "_source":['_id', 'post_title', 'post_date','post_body', 'file_extracted_content'],
            "size":100,
            "query":{
                "bool":{
                    "filter":{
                        'terms':{'hash_key':idList}
                    }
                }
            }
        }
    )
    countDoc =len(response['hits']['hits'])
    
    hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')

    for i in range(countDoc):
        postDate = response["hits"]["hits"][i]["_source"].get("post_date")
        postTitle = response["hits"]["hits"][i]["_source"].get("post_title")
        postBody= response["hits"]["hits"][i]["_source"].get("post_body")
        fileContent = response["hits"]["hits"][i]["_source"].get("file_extracted_content")
        
        fileContent = str(fileContent).replace("None",'')
        fileContent = hangul.sub('', fileContent)

        dateList.append(postDate)
        bodyList.append(postBody)
        fileList.append(fileContent)
        titleList.append(postTitle)    
    
    df['post_date'] = dateList
    df['post_title'] = titleList
    df['post_body'] = bodyList
    df['file_content'] = fileList

    df['all_content'] = df['post_body'].str.cat(df['file_content'], sep=' ', na_rep='No data')

    #print("<내 보관함>\n", df)
    #print("<내용>\n", df['all_content'][0])
    return df[['idList', 'post_date', 'all_content']]    
      
#search_in_mydoc2('21600280@handong.edu', '북한', "2021-07-08T11:46:03.973Z")
#search_in_mydoc2('21800409@handong.edu', '북한', "2021-08-04T03:48:54.395Z")

#########################################

# def search_in_mydoc(email):
#     df = pd.DataFrame()
#     idList = getMyDocByEmail(email)

#     #df['idList'] = idList
#     dateList=[]
#     bodyList=[]
#     fileList=[]    

#     ids= ['60840bc62cc126532ac77dee', '60844bc83a7fb186389bdbf6', '60844bc83a7fb186389bdbf8']
#     df['idList'] = ids

#     #hash_code로 doc_id 변경

#     #es에 있는 모든 doc 
#     res = es.search(
#         index=index,
#         body={
#             "_source":['_id', 'post_date', 'post_title'],
#             "query":{
#                 "match_all":{}
#             }
#         }
#     )

#     response=es.search( 
#         index=index, 
#         body={
#             "_source":['_id', 'post_date','post_body', 'file_extracted_content'],
#             "size":100,
#             "query":{
#                 "bool":{
#                     "filter":{
#                         'terms':{'_id':ids}
#                     }
#                 }
#             }
#         }
#     )
#     countDoc =len(response['hits']['hits'])
    
#     hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')

#     for i in range(countDoc):
#         postDate = response["hits"]["hits"][i]["_source"].get("post_date")
#         postBody= response["hits"]["hits"][i]["_source"].get("post_body")
#         fileContent = response["hits"]["hits"][i]["_source"].get("file_extracted_content")
        
#         fileContent = str(fileContent).replace("None",'')
#         fileContent = hangul.sub('', fileContent)

#         dateList.append(postDate)
#         bodyList.append(postBody)
#         fileList.append(fileContent)    
    
#     df['post_date'] = dateList
#     df['post_body'] = bodyList
#     df['file_content'] = fileList

#     df['all_content'] = df['post_body'].str.cat(df['file_content'], sep=' ', na_rep='No data')

#     '''
#         #한글 추출        
#         hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')
        
#         #데이터 전처리
#         postDate = str(postDate)
#         postYearDate = re.sub('[No date|None|^ |^-|^\n]+','None',postDate)[0:4]
#         postBody = str(postBody).replace("None",'')
#         postBody = hangul.sub('', postBody)
#         fileContent = str(fileContent).replace("None",'')
#         fileContent = hangul.sub('', fileContent)
    
#         dateList.append(postYearDate)
#         bodyList.append(postBody)
#         fileList.append(fileContent)
        
#     df['post_date'] = dateList
#     df['post_body'] = bodyList
#     df['file_content'] = fileList
 
#     #html_df = df.to_html() #flask 돌리기 위해서 
#     #csv_df = df.to_csv('es_rawdata.csv')
#     '''
#     return df[['idList', 'post_date', 'all_content']]


# #search_in_mydoc('sujinyang@handong.edu')
