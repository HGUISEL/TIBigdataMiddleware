"""
ver. 2022-04-01.
Written by yoon-ho choi.
contact: yhchoi@handong.ac.kr
"""

import ESreader.get_es_data as get_es
import cosine_similarity.cossim as cossim
import tokenizer.tokenizer as tk
import mongo_updater.mongo_updater as mu

c = get_es.get_es_data()
tk.lexical_analyze(c)
cossim.get_cosine_similarity(c)
mu.update_mongo(c)
