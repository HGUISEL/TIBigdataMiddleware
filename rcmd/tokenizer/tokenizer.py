import pandas as pd
import numpy as np

from konlpy.tag import Mecab
import re
import warnings
import os 
import time

import logging
import logging.handlers

LOG_MAX_SIZE = 1024*1024*10
LOG_FILE_CNT = 10
LOG_LEVEL = logging.INFO

warnings.filterwarnings("ignore")

def lexical_analyze(count):
    try:
        logger = logging.getLogger("rcmd")
        logfile_H = logging.handlers.RotatingFileHandler("/home/middleware/TIBigdataMiddleware/rcmd/log/rcmd.log")
        formatter = logging.Formatter('[%(asctime)s|%(levelname)s|%(funcName)s|%(lineno)d] %(message)s')
        logfile_H.setFormatter(formatter)
        logger.addHandler(logfile_H)
        logger.setLevel(LOG_LEVEL)
    except Exception as err:
        print(err)
    start = time.time()
    for i in range(0, count+1):
        df = pd.read_csv("./data/d_"+str(i)+".csv", encoding='utf-8', dtype=str)
        # 원하는 column만 추출
        df = df[['post_title', 'content', 'hashkey']]
        print("The total count of data content is " + str(len(df)))

        # 한글만 추출하기 위한 정규표현식
        hangul = re.compile('[^ \u3131-\u3163\uac00-\ud7a3]+')
        mecab = Mecab()
        tokens = []
        tokenized_word = []
        count = 0
        
        # if df['content'].isna():
        # NaN 값 있으면 오류나서 확인 후 제거
        # 제거한 값 로그에 남기기
        if df.isnull().sum().sum() > 0:
            logger.info("remove Nan rows")
            logger.info(df[df.post_title.isnull()|df.content.isnull()])
            df = df.dropna()

        for body in df['content']:
            count = count + 1
            print(count)

            # 한글만 추출
            body = hangul.sub('', body)
            for word in mecab.pos(body):
                # 일반 명사와 고유 명사만 분석
                if word[1] == 'NNG' or word[1] == 'NNP':
                    tokenized_word.append(str(word[0]))
            string = ' '.join(tokenized_word)
            tokens.append(string)
            tokenized_word = []

        df['token_body'] = pd.DataFrame(tokens)
        #print(df['token_body'])
        result = df[['post_title', 'token_body', 'hashkey']]
        os.makedirs('./tokenized/',exist_ok=True)
        result.to_csv("./tokenized/td_"+str(i)+".csv")
    print('it took',time.time()-start, ' sec.')
#lexical_analyze(1)
