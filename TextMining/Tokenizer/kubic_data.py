import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname('TextMining/Tokenizer'))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname('TextMining/Analyzer'))))

from elasticsearch import Elasticsearch

import TextMining.Tokenizer.esAccount as esAcc 
from TextMining.Tokenizer.kubic_mystorage import *#
#from TextMining.Tokenizer.kubic_mystorage import getMyDocByEmail2

#python app.py하면 문제,,
# import esAccount as esAcc
# from kubic_mystorage import *


from ssl import create_default_context
import re
import pandas as pd

import traceback

es = Elasticsearch(
        [esAcc.host],
        http_auth=(esAcc.id, esAcc.password),
        scheme="https",
        port= esAcc.port,
        verify_certs=False # 이거 왜 해야하는고야
)
index = esAcc.index

## Collect data from es(post_title, post_date, post_body, file_content) and return dataframe
def search_in_mydoc_add_title(email, keyword, savedDate):
    #savedDate = datetime.datetime.strptime(savedDate, "%Y-%m-%dT%H:%M:%S.%fZ")
    idList = getMyDocByEmail2(email, keyword, savedDate) # es애서 삭제된 id도 포함
    try:
        print(idList)
        if idList[0] == 'failed':
            return 'failed', idList[1]
    except Exception as e:
        return 'failed', "getMyDocByEmail2의 리턴형식이 맞지 않습니다. "

    try:
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
    except Exception as e:
        err = traceback.format_exc()
        print(err)
        return 'failed', "search_in_mydoc_add_title: es search에서 문제가 생겼습니다. \n 세부사항: "+str(e)   
    
    try:
        countDoc =len(response['hits']['hits'])
    
        # 실제로 받아온 response 에 근거하여, idlist 를 새로 만듦

        # hangul = re.compile('[^ ㄱ-ㅣ가-힣]+') 영어 및 특수문자 추가
        hangul = re.compile('[^ [\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"a-zA-Z0-9ㄱ-ㅣ가-힣]+')

        idList=[]
        dateList=[]
        bodyList=[]
        fileList=[]    
        titleList=[]

        for i in range(countDoc):
            docId = response["hits"]["hits"][i]["_source"].get("_id")
            postDate = response["hits"]["hits"][i]["_source"].get("post_date")
            postTitle = response["hits"]["hits"][i]["_source"].get("post_title")
            postBody= response["hits"]["hits"][i]["_source"].get("post_body")
            fileContent = response["hits"]["hits"][i]["_source"].get("file_extracted_content")
            
            # 빈 내용 공백처리
            postBody = str(postBody).replace("None",' ')
            postBody = hangul.sub('', postBody)
            # 문장부호로 문장단위 끊기
            postBody = re.split('[.!?]', postBody)
            
            # 빈 내용 공백처리
            fileContent = str(fileContent).replace("None",' ')
            fileContent = hangul.sub('', fileContent)
            # 문장부호로 문장단위 끊기
            fileContent = re.split('[.!?]', fileContent)

            idList.append(docId)
            dateList.append(postDate)
            bodyList.append(postBody)
            fileList.append(fileContent)
            titleList.append(postTitle)

    except Exception as e:
        err = traceback.format_exc()
        print(err)
        return 'failed', "search_in_mydoc_add_title: es search 후 구조화 과정에서 문제가 생겼습니다. \n 세부사항: "+str(e)    
    

    try:
        allContentList = []
        for i in range(len(bodyList)):
            sentenceList = bodyList[i] + fileList[i]
            allContentList.append(sentenceList)
    except Exception as e:
        err = traceback.format_exc()
        print(err)
        return 'failed', "search_in_mydoc_add_title: 문서 내용 리스트 생성 중 오류가 발생했습니다. \n 세부사항: "+str(e)  
    df = pd.DataFrame()
    df['idList'] = idList
    df['post_date'] = dateList
    df['post_title'] = titleList
    df['post_body'] = bodyList
    df['file_content'] = fileList
    df['all_content'] = allContentList

    return True, df[['idList', 'post_date', 'all_content', 'post_title', 'post_body']]

# result, df = search_in_mydoc_add_title('21800520@handong.ac.kr', '올림픽', "2022-05-16T14:39:08.448Z")
# if result == True:
#     print(df['all_content'])
# else:
#     print(df)
