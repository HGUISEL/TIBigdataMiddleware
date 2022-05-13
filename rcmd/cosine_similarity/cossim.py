"""
ver. 2022-04-01.
Written by yoon-ho choi.
contact: yhchoi@handong.ac.kr
"""
import random
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time
import sys

def chunk_iterator(files):
    for f in files:
        for chunk in pd.read_csv(f, chunksize=1000, encoding='utf-8', dtype=str, low_memory=False):
            if chunk.isnull().values.any():
                chunk = chunk.dropna(how='any')
            for doc in chunk['token_body'].values:
                yield doc

def get_cosine_similarity(count):
    start = time.time()
    similarity = []
    files = []
    hash_key = []
    for i in range(0, count+1):
        files.append("./tokenized/td_"+str(i)+".csv")
        df = pd.read_csv("./tokenized/td_"+str(i)+".csv",encoding='utf-8', dtype=str, low_memory=False)
        if df.isnull().values.any():
            df = df.dropna(how='any')
        hash_key.extend(df['hashkey'].values.tolist())
    
    corpus = chunk_iterator(files)
    #print(df['token_body'][0:2]) 
    # TF-IDF 벡터를 만듬
    start_tfidf = time.time()
    tfidf = TfidfVectorizer()
    print('Start TF-IDF vectorizing...')
    tfidf_matrix = tfidf.fit_transform(corpus)
    print('hashkey list:', len(hash_key))
    print('The shape of TF-IDF matrix is ', tfidf_matrix.shape)
    print('it took', time.time() - start_tfidf,' sec.')
    print('Start computing Cosine similarity...')
    # cosine similarity 연산
    start_cos = time.time()
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    print('it took', time.time() - start_cos,' sec.')
    print("tfidf2cos_time: ", time.time() - start_tfidf, "sec.")
    #print('The shape of cosine similarity is ', cosine_sim.shape)
    
    print('Start sorting and ranking...')
    start_sort = time.time()
    key_sim_pair = []  
    for i in range(len(cosine_sim)):
        tmp_pair = []
        for j in range(len(cosine_sim[i])):
            if(hash_key[i] == hash_key[j]):
                continue
            tmp_pair.append((hash_key[j], cosine_sim[i][j]))
        #descending order
        tmp_pair.sort(key=lambda x:x[1], reverse=True)
        key_sim_pair.append([hash_key[i], tmp_pair[0:5]])
        if(i % 1000 == 0):
            print('current: ',i)
    print('It took ', time.time()-start_sort, 'sec.')
    
    #print('Start collecting top five...')
    #similarity = []
    #for i in range(len(key_sim_pair)):
    #    similarity.append([hash_key[i], key_sim_pair[i][0:5]])
    #    if(i % 1000 == 0):
    #        print('current: ',i)
        #for j in range(len(cosine_sim[i])):
        #    cosine_sim[i][j].sort(reverse=True)
        #    # 연관된 문서만
        #    if cosine_sim[i][j] > 0:
        #        similarity.append([hash_key[i], hash_key[j], cosine_sim[i][j]])
    #print(i)
    print("tfidf2doc_time: ", time.time() - start_tfidf, "sec.")    
    print("cos2doc_time: ", time.time() - start_cos, "sec.")
    print(len(key_sim_pair))

    result = pd.DataFrame(key_sim_pair, columns=['hashKey', 'rcmdDocID,Score'])
    result.to_csv("rcmdsFinal.csv", index=True)

#get_cosine_similarity(1)
