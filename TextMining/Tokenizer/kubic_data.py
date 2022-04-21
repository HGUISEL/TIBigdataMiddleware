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

## Collect data from es(post_date, post_body, file_content) and return dataframe
def search_in_mydoc2(email, keyword, savedDate):
    #savedDate = datetime.datetime.strptime(savedDate, "%Y-%m-%dT%H:%M:%S.%fZ")
    idList = getMyDocByEmail2(email, keyword, savedDate) # es애서 삭제된 id도 포함
    print('idList=', idList)

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
    
    # 실제로 받아온 response 에 근거하여, idlist 를 새로 만듦

    hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')

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
        
        fileContent = str(fileContent).replace("None",'')
        fileContent = hangul.sub('', fileContent)

        idList.append(docId)
        dateList.append(postDate)
        bodyList.append(postBody)
        fileList.append(fileContent)
        titleList.append(postTitle)    
    
    df = pd.DataFrame()
    df['idList'] = idList
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
            
            fileContent = str(fileContent).replace("None",'')
            fileContent = hangul.sub('', fileContent)

            # 문장부호로 문장단위 끊기
            fileContent = re.split('[.!?]', fileContent)

            idList.append(docId)
            dateList.append(postDate)
            bodyList.append(postBody)
            fileList.append(fileContent)
            titleList.append(postTitle)

    except Exception as e:
        return 'failed', "search_in_mydoc_add_title: es search 후 구조화 과정에서 문제가 생겼습니다. \n 세부사항: "+str(e)    
    
    df = pd.DataFrame()
    df['idList'] = idList
    df['post_date'] = dateList
    df['post_title'] = titleList
    df['post_body'] = bodyList
    df['file_content'] = fileList
    df['all_content'] = df['file_content']
    #df['all_content'] = df['post_body'].str.cat(df['file_content'], sep=' ', na_rep='No data')

    return True, df[['idList', 'post_date', 'all_content', 'post_title', 'post_body']]

# result, df = search_in_mydoc_add_title('21800520@handong.edu', '북한', "2021-09-07T07:01:07.137Z")
# print(df["all_content"][0])

##############################################################################################################
def search_in_mydoc_for_research(email, keyword, savedDate, kkma = False):
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
                "_source":['hash_key', 'post_title', 'post_date','post_body', 'file_extracted_content'],
                "size":2000
            }
        )
    except Exception as e:
        err = traceback.format_exc()
        print(err)
        return 'failed', "search_in_mydoc_add_title: es search에서 문제가 생겼습니다. \n 세부사항: "+str(e)   
    

    countDoc =len(response['hits']['hits'])
    print(countDoc)

    # 실제로 받아온 response 에 근거하여, idlist 를 새로 만듦

    hangul = re.compile('[^ ,;:?.!ㄱ-ㅣ가-힣]+') 
    # hangul = re.compile('[^ [\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"a-zA-Z0-9ㄱ-ㅣ가-힣]+') 영어 및 특수문자 추가

    idList=[]
    dateList=[]
    bodyList=[]
    fileList=[]    
    titleList=[]

    def isKorean(input_s):
        k_count = 0
        e_count = 0
        else_count = 0
        for c in input_s:
            if ord('가') <= ord(c) <= ord('힣'):
                k_count+=1
            elif ord('a') <= ord(c.lower()) <= ord('z'):
                e_count+=1
            else:
                else_count +=1
        if  k_count>e_count and k_count>else_count:
            return True
        else:
            return False

    for i in range(countDoc):
        docId = response["hits"]["hits"][i]["_source"].get("hash_key")
        postDate = response["hits"]["hits"][i]["_source"].get("post_date")
        postTitle = response["hits"]["hits"][i]["_source"].get("post_title")
        postBody= response["hits"]["hits"][i]["_source"].get("post_body")
        fileContent = response["hits"]["hits"][i]["_source"].get("file_extracted_content")
        # myText = open('/home/middleware/TIBigdataMiddleware/TextMining/Tokenizer/test.txt','w')
        # myString = str(response["hits"]["hits"][i])
        # myText.write(myString)
        # myText.close()
        # return True, True

        if postTitle == None or fileContent == None:
            continue
        if len(fileContent) < 100 :
            continue
        if not isKorean(postTitle):
            continue

        fileContent = str(fileContent).replace("None",'')
        fileContent = hangul.sub('', fileContent)

        # 문장부호로 문장단위 끊기
        fileContent = re.split('[.!?]', fileContent)
        idList.append(docId)
        dateList.append(postDate)
        bodyList.append(postBody)
        fileList.append(fileContent)
        titleList.append(postTitle)

        if len(idList) > 100:
            break

    df = pd.DataFrame()
    df['idList'] = idList
    df['post_date'] = dateList
    df['post_title'] = titleList
    df['post_body'] = bodyList
    df['file_content'] = fileList
    df['all_content'] = df['file_content']
    #df['all_content'] = df['post_body'].str.cat(df['file_content'], sep=' ', na_rep='No data')

    # df.to_csv('/home/middleware/TIBigdataMiddleware/TextMining/Tokenizer/datas.csv', sep=',', na_rep='NaN')

    return True, df[['idList', 'post_date', 'all_content', 'post_title', 'post_body']]

# result, df = search_in_mydoc_for_research('21800520@handong.edu', '북한', "2021-09-07T07:01:07.137Z")
# try:
#     print(df["all_content"])
# except:
#     print(df)