
import json
DIR_FE = "../Front_KUBIC/src/assets/homes_graph/data.json"

def textrank():
    from konlpy.tag import Okt
    from gensim.summarization import keywords

    okt = Okt() # 형태소 분석기

    with open("krWl.txt", "r" ,encoding='utf-8') as f: #1개 파일 로드
        texts = f.read() 

    tokenized_doc = okt.nouns(texts) # 형태소 분석해서 단어 쪼갬. return array
    tokenized_doc = ' '.join(tokenized_doc)  # 형태소 분석을 textrank 적용위해서 쉼표로 분리된 하나의 string으로.

    result = keywords(tokenized_doc, words = 15 , scores=True)

    with open(DIR_FE, 'w', -1, "utf-8") as f: # 데이터 파일 저장
        json.dump(result, f, ensure_ascii=False)

    return result

