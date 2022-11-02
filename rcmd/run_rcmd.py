"""
ver. 2022-04-01.
Written by yoon-ho choi.
contact: yhchoi@handong.ac.kr
"""
"""
ver. 2022-09-22.
Updated by sung-won lee.
contact: 21800520@handong.ac.kr
"""


import ESreader.get_es_data as get_es
import cosine_similarity.cossim as cossim
import tokenizer.tokenizer as tk
import mongo_updater.mongo_updater as mu


# c = 문서 수//10000
# Paper
c = get_es.get_es_data("Paper")
tk.lexical_analyze(c)
cossim.get_cosine_similarity(c)
mu.update_mongo(2, resetMongo = True)

# News
c = get_es.get_es_data("News")
tk.lexical_analyze(c)
cossim.get_cosine_similarity(c)
mu.update_mongo(c)