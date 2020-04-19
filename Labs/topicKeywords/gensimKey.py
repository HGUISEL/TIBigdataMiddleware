import json


from gensim.summarization import keywords


def gensimKey():
    DIR_FE = "../../../TIBigdataFE/src/assets/special_first/ctgRNNResult.json"

    with open(DIR_FE, 'r', encoding='utf-8') as fp:
        data = json.load(fp)

    totalStr = ""
    for i in range(len(data)):

        corpus = data[i]["doc"]

        isTokened = True

        if isTokened == True:
            print("\ntopic : ",data[i]["topic"])
            print("num of docs : ", len(corpus))
            import traceback
            import sys
            # count = 0
            # tokenized_doc = []
            oneStr = ""
            for j, doc in enumerate(corpus):
                oneStr += doc["words"]
                # try:
                #     tokenized_doc.append(doc["words"])
                #     # print(tokenized_doc[0])
                #     result = keywords(doc["words"], words=15, scores=True)
                #     # print(result)
                # except Exception as e:
                #     result = keywords(doc["words"], words=10, scores=True)
                # except:
                #     traceback.print_exc()
                #     # print('Error: {}. {}.{}'.format(sys.exc_info()[0],
                #             # sys.exc_info()[1],sys.exc_info()[2]))
                #     print("error in : ", j)
                #     print(doc["words"],"\n")
                # " ".join()
            # result = keywords(oneStr, words=15, scores=True)
            # print(result)
            # with open("./wr"+data[i]["topic"]+".json", 'w', -1, "utf-8") as f:
            #     json.dump(result, f, ensure_ascii=False)
            totalStr += oneStr
        else:
            contents = []
            for doc in corpus:
                contents.append(doc["contents"])

            tagger = Mecab()
            print("데이터 전처리 중... It may takes few hours...")
            tokenized_doc = [tagger.nouns(contents[cnt])
                            for cnt in range(len(contents))]
    result = keywords(totalStr, words=15, scores=True)
    print(result)
    with open("./wr"+"total"+".json", 'w', -1, "utf-8") as f:
        json.dump(result, f, ensure_ascii=False)
    # with open("krWl.txt", "r" ,encoding='utf-8') as f:
    #     texts = f.read()
        # print(f.read())
        # tokenized_doc = tagger.nouns(texts)
        # tokenized_doc = ' '.join(tokenized_doc)
        # print("형태소 분석 이후 단어 토큰의 개수",len(tokenized_doc))

    # result = keywords(tokenized_doc[0], words=15, scores=True)
    # print(result)
    # with open(DIR_FE, 'w', -1, "utf-8") as f:
    

    return json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    gensimKey()
