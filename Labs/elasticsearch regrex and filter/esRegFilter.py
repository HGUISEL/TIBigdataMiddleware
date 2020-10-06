from elasticsearch import Elasticsearch
import json

DB_URL = "http://203.252.112.14:9200/" + "nkdb200810"
es = Elasticsearch(DB_URL)
# es = Elasticsearch(timeout=30)

body = {}

"""
    post_Date가 있는 문서 수 확인
"""
if False:
    body["query"] = {"exists": {"field": "post_date"}}

    #count
    res_isDate = es.count(body)
    body["query"] = {"match_all": {}}
    res_all = es.count(body)
    print(str(res_isDate["count"]) + " docs have post_date field out of " + str(res_all["count"]))

    """
        nkdb200810
        post_date가 있는 문서 898 out of 9??
        없는 문서

        nkdb200811
        post_date가 있는 문서 9999 out of 13???
    """




"""
    regex 적용해보기
"""
if False:
    # body = {"query" : {"regexp" : {"post_date" : {"[0-9]{4}-[0-9]{2}-[0-9]{2}",}}}}
    # body["query"] = {"regexp": {"post_date": {"value" : "[0-9]{4}-[0-9]{2}-[0-9]{2}",}}}
    body["query"] = {"regexp": {"post_date": {"value" : "[0-9]{4}",}}}
    body["_source"] = ["post_date"]
    body["size"] =  1000
    # body += json.dumps(query)


    """
        실제... post_date 출력해보기.
        이제 여기서... regrex 을 적용해보기.
        app 에서 상원이 로직 가지고 오기
    """

    #search
    res = es.search(body)["hits"]["hits"]
    # print(res[0])
    # # count_s = 0
    count = 0
    for doc in res:
        data = doc["_source"]["post_date"]
        print(data)
        try:
            print(data)
            # count += 1
            # if count > 10:
            #     break
        except:
            count += 1
            print("ERROR! count : ", count)
    #     # print(type(date))
    print("error count : ", count)
    #     # t = type(date)
    #     # if date == "string":



"""
    합치기 위해서 elasticsaerch aggregation을 사용해보기
"""
if False:
    aggs1 = {"regexp": {"post_date": {"value" : "[0-9]{4}",}}}

    body["aggs"] = {
        "reg" : aggs1
    }
    body["size"] =  1000




    res = es.search(body)
    print(res)
    # res = es.search(body)["hits"]["hits"]
    # count = 0
    # for doc in res:
    #     data = doc["_source"]["post_date"]
    #     print(data)
    #     try:
    #         print(data)
    #         # count += 1
    #         # if count > 10:
    #         #     break
    #     except:
    #         count += 1
    #         print("ERROR! count : ", count)
    # #     # print(type(date))
    # print("error count : ", count)



"""
    regex 적용해보기 with ... 
"""
if False:
    # body = {"query" : {"regexp" : {"post_date" : {"[0-9]{4}-[0-9]{2}-[0-9]{2}",}}}}
    # body["query"] = {"regexp": {"post_date": {"value" : "[0-9]{4}-[0-9]{2}-[0-9]{2}",}}}
    body["query"] = {"regexp": {"post_date": {"value" : "[0-9]{4}",}}}
    body["_source"] = ["post_date"]
    body["size"] =  1000
    # body += json.dumps(query)


    """
        실제... post_date 출력해보기.
        이제 여기서... regrex 을 적용해보기.
        app 에서 상원이 로직 가지고 오기
    """

    #search
    res = es.search(body)["hits"]["hits"]
    # print(res[0])
    # # count_s = 0
    count = 0
    for doc in res:
        data = doc["_source"]["post_date"]
        print(data)
        try:
            print(data)
            # count += 1
            # if count > 10:
            #     break
        except:
            count += 1
            print("ERROR! count : ", count)
    #     # print(type(date))
    print("error count : ", count)
    #     # t = type(date)
    #     # if date == "string":


