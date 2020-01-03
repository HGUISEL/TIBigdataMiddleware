# import esFunc

# esFunc.esGetADoc()

# from krwordrank.hangle import normalize


# texts = ['이것은 예문입니다', '각자의 데이터를 준비하세요', ... ]
# texts = [normalize(text, english=True, number=True) for text in texts]

# import re
# m = re.search('(?<=abc)def', 'abcdef')
# print(m.group(0))
# print(re._pattern_type)
# print(re.Pa)


# La La Land
# def get_texts_scores(fname):
#     with open(fname, encoding='utf-8') as f:
#         docs = [doc.lower().replace('\n','').split('\t') for doc in f]
#         docs = [doc for doc in docs if len(doc) == 2]
        
#         if not docs:
#             return [], []
        
#         texts, scores = zip(*docs)
#         return list(texts), list(scores)

# fname = './krWL.txt'
# texts, scores = get_texts_scores(fname)

# from krwordrank.word import KRWordRank
# from krwordrank.hangle import normalize
# import krwordrank
# print(krwordrank.__version__)

# wordrank_extractor = KRWordRank(
#     min_count = 5, # 단어의 최소 출현 빈도수 (그래프 생성 시)
#     max_length = 10, # 단어의 최대 길이
#     verbose = True
#     )

# beta = 0.85    # PageRank의 decaying factor beta
# max_iter = 10

# keywords, rank, graph = wordrank_extractor.extract(texts, beta, max_iter)





#############################TEXTRANK KOREAN WORK!###########################
# from konlpy.tag import Okt
# from gensim.summarization import keywords

# okt = Okt()

# with open("krWl.txt", "r" ,encoding='utf-8') as f:
#     texts = f.read() 
#     # print(f.read())
# tokenized_doc = okt.nouns(texts)
# tokenized_doc = ' '.join(tokenized_doc) 
# print(tokenized_doc) 

# print(keywords(tokenized_doc, words = 20 , scores=True))
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

    # print(keywords(tokenized_doc, words = 20 , scores=True))
    result = keywords(tokenized_doc, words = 15 , scores=True)
    with open(DIR_FE, 'w', -1, "utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    return result

# import LDA as lda
# lda.LDA()


# tu = [(0, 0), (1, 1), (2, 0), (3, 2), (4, 0), (5, 0), (6, 2), (7, 1), (8, 0), (9, 2), (10, 0), (11, 0), (12, 1), (13, 1), (14, 1), (15, 1), (16, 2), (17, 1), (18, 0)]
# print(tu[2][1])