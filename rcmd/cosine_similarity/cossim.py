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

import csv

DOC_NUM_OF_A_SET = 10000

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

    print('Start computing, sorting and ranking Cosine similarity...')
    
    start_cos = time.time()
    for i in range(count+1):
        print('current: set#'+str(i))
        start_cos_set = time.time()
        # cosine similarity 연산
        print('\t computing cosine_similarity')
        start_comp = time.time()
        if i == count:
            cosine_sim = cosine_similarity(tfidf_matrix[i*DOC_NUM_OF_A_SET:,], tfidf_matrix) 
        else:
            cosine_sim = cosine_similarity(tfidf_matrix[i*DOC_NUM_OF_A_SET:(i+1)*DOC_NUM_OF_A_SET,], tfidf_matrix) 
        print('\t It took ', time.time()-start_comp, 'sec.')
        start_sort = time.time()
        key_sim_pair = []
        print('\t sorting cosine_similarity')
        for k in range(len(cosine_sim)):
            tmp_pair = []
            for j in range(len(cosine_sim[k])):
                if not (hash_key[i*DOC_NUM_OF_A_SET+k] == hash_key[j]):
                    tmp_pair.append((hash_key[j], cosine_sim[k][j]))
            #descending order
            tmp_pair.sort(key=lambda x:x[1], reverse=True)
            key_sim_pair.append([hash_key[i*DOC_NUM_OF_A_SET+k], tmp_pair[0:5]])
        print('\t It took ', time.time()-start_sort, 'sec.')

        start_cos_set = time.time()
        result = pd.DataFrame(key_sim_pair, columns=['hashKey', 'rcmdDocID,Score'])
        result.to_csv("./rcmdFinal/rcmdsFinal_news"+str(i)+".csv", index=True)
        print(' Set#'+str(i),'took ', time.time()-start_cos_set, 'sec.')
    
    print("tfidf2doc_time: ", time.time() - start_tfidf, "sec.")    
    print("cos2doc_time: ", time.time() - start_cos, "sec.")



#get_cosine_similarity(1)
