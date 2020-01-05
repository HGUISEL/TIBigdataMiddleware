############################TEXTRANK KOREAN WORK!###########################
# from konlpy.tag import Okt
# from gensim.summarization import keywords

# okt = Okt()

# with open("krWl.txt", "r" ,encoding='utf-8') as f:
#     texts = f.read() 
#     # print(f.read())
# tokenized_doc = okt.nouns(texts)
# tokenized_doc = ' '.join(tokenized_doc) 
# print(tokenized_doc) 

# # print(keywords(tokenized_doc, words = 20 , scores=True))
import json
DIR_FE = "../Front_KUBIC/src/assets/homes_graph/data.json"

def textrank():
    from konlpy.tag import Okt
    from gensim.summarization import keywords

    okt = Okt()

    with open("krWl.txt", "r" ,encoding='utf-8') as f:
        texts = f.read() 
        # print(f.read())
    tokenized_doc = okt.nouns(texts)
    tokenized_doc = ' '.join(tokenized_doc) 
    print(len(tokenized_doc)) 

    result = keywords(tokenized_doc, words = 15 , scores=True)
    with open(DIR_FE, 'w', -1, "utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    return result