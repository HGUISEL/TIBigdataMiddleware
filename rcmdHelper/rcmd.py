## phase 0. 디렉토리 추가
## 현재 위치 : .\TIBigdataMiddleware\cosSim\

## 다른 모듈을 사용하기 위해  TIBigdataMiddleware 추가
## middleware home에도 dir 추가
from pathlib import Path
import os
curDir = os.getcwd()
curDir = Path(curDir)
homeDir = curDir.parent
# # comDir = homeDir / "common"

import sys
sys.path.append(str(homeDir))
# os.chdir(str(homeDir))
# print(str(homeDir))

## 다른 모듈에 사용 받기 위해 현재 이 디렉토리 추가
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)


# static directory
TFIDF_DIR = "./rcmdHelper/skl_tfidf.json"
DATA_DIR = "./rcmdHelper/data.json"


NDOC = 10000
# # else:
# # phase 1-2: 저장되어 있는 tf-idf 값과 data 정보 불러옴
# import json
# with open(TFIDF_DIR, 'r') as fp:
#     cosine_sim = json.load(fp)
# with open(DATA_DIR, 'r',encoding="utf-8") as fp:
#     data = json.load(fp)
# print("rcmd file loaded!")


"""
# fnction : create_similiarity_matrix(data)
# purpose : 전달받은 BoW에 대한 코사인 유사도 테이블을 만든다. sk-learn TF-IDF 사용. matrix형태로 나온다.
# input : dictionary : 
        {"id" : idList, "titles" : titles, "contents" : contents}
# output : array
            [
                [문서 1의 단어 TF-IDF 값들],
                [문서 2의 단어 TF-IDF 값들],
                ...
            ]
"""
def create_similiarity_matrix(data = None):

    # if(data == None):
    #     from common import prs
    #     data = prs.loadData(NDOC)

        # 쿼리 데이터 파일로 저장
        # import json
        # with open(DATA_DIR, 'w',encoding="utf-8") as fp:
            # json.dump(data, fp,ensure_ascii=False)

    # global cosine_sim
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import linear_kernel
    tfidf = TfidfVectorizer()
    for i, d in reversed(list(enumerate(data))):
        # if(i < 10):
        #     print(d)
        if d ==None:
            print(d)
            data.pop(i)
    tfidf_mtx = tfidf.fit_transform(data)

    cosine_sim = linear_kernel(tfidf_mtx, tfidf_mtx)

    # save tfidf result
    # import json
    # with open(TFIDF_DIR, 'w',encoding="utf-8") as fp:
    #     json.dump(cosine_sim.tolist(), fp,ensure_ascii=False)


    return cosine_sim

    
"""
* **function : sort_similiarity_table()**
  * purpose : 각 tfidf 테이블을 정렬하는 작업
            현재 상태는 문서의 순서대로 각 문서의 연관 문서가 list에 들어가 있다.
            연관문서를 표현하려면 연관순위가 높은 문서들을 표시해야 하므로,
            문서 유사도가 높은 문서들을 앞으로 정렬한다.

"""

def sort_similiarity_table(sim_id_merge):
        import operator
        
        sort_merge = []
                                                 # for loop에서 type 변환해서 저장하는게 안되는 모양?
        for i,oneDocSimID in enumerate(sim_id_merge):#for loop안에서 list element 새로 assgin => index으로 접근. 
                                                 #for i, oneDocRec에서 oneDocRec은 local var이다.
            oneDocRec = list(enumerate(oneDocSimID["rcmd"]))
            # print(type(oneDocRec))
            oneDocSimID["rcmd"] = sorted(oneDocRec, key=lambda x: x[1], reverse=True)
            sort_merge.append(oneDocSimID)

        # using map
        # sort_cos_sim = map(lambda x : sorted(list(enumerate(x)), key=operator.itemgetter(1), reverse=True),cosine_sim)
        # print(sort_cos_sim[0])

        # save result
        # with open(TFIDF_DIR, 'w') as fp:
        #     json.dump(sort_cos_sim, fp)
        return sort_merge



def merge_data_sim(ID_list, sim_table):

    if len(ID_list) != len(sim_table):
        raise Exception("문서의 갯수가 맞지 않아요.")
    # for idx, docRec in enumerate(oneDocRec):
    #     oneDocRec

    merge = []
    for i,oneDocRec in enumerate(sim_table):
        merge.append({"docID" : ID_list[i], "rcmd" : oneDocRec})
        # print(oneDocRec)
        # for j, oneRec in enumerate(oneDocRec):
            # print("ID_List[i] =" , ID_list[i])
            # print(oneRec)
            # oneRec[0] = ID_list[i]
    # print(merge)
    return merge


# def create_similiarity(data=None):
#     cosine_sim = create_similiarity_matrix(data)
#     return sort_similiarity_table(cosine_sim)

"""
* **function : create_recommand(idList, calc_again = False)**
  * purpose : 전달받은 문서들의 관련문서들을 찍어준다.
  * input : 문서 id list<string>. 연관 문서를 얻으려는 문서들 list
  * output : dictionary 
            {
                "id" : "abcde", 
                "rcmd" : [ [doc_number,  "B", "C", "D", "E" ], 
                 #"address" : [ "A", "B", "C", "D", "E" ]#
            }
               
  * NOTICE : 
    * calc_again = True으로 호출하면 새로 서버에서 문서를 로드해서 tf-idf 데이터를 저장하고, 
                새로운 결과로 프론트엔드에 전달한다.
    * calc_again = false으로 호출하면 기존에 저장해둔 정보를 사용한다. 빠르게 프론트엔드에 응답해준다. defualt값.
"""
def create_recommand():
    from cmm import showTime
    from cmm import startTime
    start = startTime()
    # global data
    # global cosine_sim


    # # phase 1: TF-IDF을 새로 업데이트하여 출력할 것인지 결정
    # if calc_again == True:
    # # phase 1-1: 문서 로드 및 새로 tfidf 테이블을 만든다.
    #    create_similiarity()
      

    # # # phase 1-2: 저장되어 있는 tf-idf 값과 data 정보 불러옴
    # else:
    #     import json
    #     try:
    #         with open(TFIDF_DIR, 'r') as fp:
    #             cosine_sim = json.load(fp)
    #         with open(DATA_DIR, 'r',encoding="utf-8") as fp:
    #             data = json.load(fp)
    #     except:# 이미 저장되어 있는 파일이 없거나 에러가 발생해서 다시 테이블을 만들어야 할 때!
    #         print("Load pre-existing analysis data failed. Execute new analysis data again...")
    #         create_similiarity()

    # 쿼리 기본 데이터 필요
    #Query docs from es then prs, OR, use latest prs
    if False:
        from common import prs
        data = prs.loadData(NDOC)
    else:
        import json
        with open('../latestPrsResult/latest_corpus_with_id_witle_contents.json', 'r') as f:
            data = json.load(f)
    print("문서 로드 완료!")


    ID_list = data["id"]
    contents = data["contents"]
    # 코사인 유사도 테이블 필요

    # cosine_sim = create_similiarity_matrix(contents)
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import linear_kernel
    tfidf = TfidfVectorizer()
    for i, d in reversed(list(enumerate(contents))):
        # if(i < 10):
        #     print(d)
        if d ==None:
            print(d)
            contents.pop(i)
    tfidf_mtx = tfidf.fit_transform(contents)

    cosine_sim = linear_kernel(tfidf_mtx, tfidf_mtx)
    # print(cosine_sim)

    # sim_id_merge = merge_data_sim(ID_list, cosine_sim)
    if len(ID_list) != len(cosine_sim):
        raise Exception("문서의 갯수가 맞지 않아요. len(ID_list) = ",len(ID_list), "len(cosine_sim) = ", len(cosine_sim))
    # for idx, docRec in enumerate(oneDocRec):
    #     oneDocRec

    rcmdTable = []
    for i,rcmdForOneDoc in enumerate(cosine_sim):
        tupleList = []
        for j, rcmdVal in enumerate(rcmdForOneDoc):
            tupleList.append((ID_list[j], rcmdVal))
        tupleList = sorted(tupleList, key=lambda x: x[1], reverse=True)#sort by high similarity value
        # if i < 3:
        #     print(tupleList)
        rcmdTable.append({"docID" : ID_list[i], "rcmd" : tupleList})
        # oneDocRec = list(enumerate(oneDocSimID["rcmd"]))
        # print(type(oneDocRec))
        # oneDocSimID["rcmd"] = sorted(oneDocRec, key=lambda x: x[1], reverse=True)
    # print(sim_with_id_mapping)
    return rcmdTable
    # merge = []
    # for i,oneDocRec in enumerate(cosine_sim):
    #     merge.append({"docID" : ID_list[i], "rcmd" : oneDocRec})


    # # sort_sim = sort_similiarity_table(sim_id_merge)
    # import operator
        
    # sort_merge = []
    #                                             # for loop에서 type 변환해서 저장하는게 안되는 모양?
    # for i,oneDocSimID in enumerate(merge):#for loop안에서 list element 새로 assgin => index으로 접근. 
    #                                             #for i, oneDocRec에서 oneDocRec은 local var이다.

    #     rcmd = oneDocSimID["rcmd"]
    #     # print(rcmd)
    #     for j, rc in enumerate(rcmd):
    #         rcmd[j] = (ID_list[j], rc)
    #         # print(rc)
    #     print(rcmd)
        # oneDocRec = list(enumerate(oneDocSimID["rcmd"]))
        # print(type(oneDocRec))
        # oneDocSimID["rcmd"] = sorted(oneDocRec, key=lambda x: x[1], reverse=True)
        # sort_merge.append(oneDocSimID)
    # print(merge)
    # for mergeDoc in sort_merge:
    #     for rcmd in mergeDoc["rcmd"]:
    #         docIdx = rcmd[0]
    #         rcmd[0] = ID_list[docIdx]
            # print(type(rcmd[0]))
            # print(type(ID_list[docIdx]))
            # try:
            # except:
            #     print(rcmd[0])
            #     print(ID_list[docIdx])
    
    # return sort_merge


    # using map
    # sort_cos_sim = map(lambda x : sorted(list(enumerate(x)), key=operator.itemgetter(1), reverse=True),cosine_sim)
    # print(sort_cos_sim[0])

    # save result
    # with open(TFIDF_DIR, 'w') as fp:
    #     json.dump(sort_cos_sim, fp)
    # return sort_merge



    # showTime(start)
    # return sort_sim

    # print(sort_sim)
    # # FE에서 요청한 각 문서가 cossinSim 리스트의 몇번째 문서인지 파악해야 한다.
    # ids = data["id"]
    # # print(ids)

    # import traceback

    # rcmdListAll = []
    # for id in idList:
    #     try:
    #         index = ids.index(id)# FE에서 요청한 각 문서의 index을 파악

    #         #recommendation table
    #         rcmdTbl = cosine_sim[index]
            
    #         rcmdList = []
    #         rcmdListId = []
    #         for i, oneRcmd in enumerate(rcmdTbl):
    #             if i > 5:
    #                 break
    #             docIdx = oneRcmd[0]#몇번째 문서인지 알려준다.
    #             rcmdList.append(data["titles"][docIdx])#제목을 담기
    #             rcmdListId.append(data["id"][docIdx])

    #         rcmdListAll.append({"id" : rcmdListId, "rcmd" : rcmdList})
    #     except Exception as e:
    #     # traceback.print_exc()
    #         print('Error: {}. {}'.format(sys.exc_info()[0],
    #                 sys.exc_info()[1]))
    #         print("error at id ", id)
    
    # showTime(start)

    # return rcmdListAll



if __name__ == "__main__":
    from common import prs

    # data = prs.loadData(1000)
    # cosine_sim = create_similiarity_matrix()
    # print(cosine_sim)
    # print(type(cosine_sim))
    sim_table = create_recommand()
    # print(sim_table)
    import pymongo
    from pymongo import MongoClient
    import json
    client = MongoClient('localhost',27017)
    db = client.analysis0919
    collection = db.rcmds
    collection.insert_many(sim_table)
    



