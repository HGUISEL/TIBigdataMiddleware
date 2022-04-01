import pandas as pd
from tqdm import tqdm
import numpy as np
import json
import os
import csv
import time
import os.path
import traceback
import sys
import re
import logging
from topic_analysis.__get_logger import __get_logger

if os.name == "nt":# 윈도우 운영체제
    from eunjeon import Mecab
else:# 현재 리눅스 서버 및 맥은 konlpy으로 미캡 모듈 import
    from konlpy.tag import Mecab

#### 토큰화해주는 함수 ####
def dataPrePrcs(contents):
    no_kor_num=0
    logger=__get_logger()

    try:
        logger.info('mecab 형태소 분석기를 실행합니다.')
        tagger = Mecab()
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)#+"\n"+ str(trace_back)
        logger.error('mecab형태소 분석기 실행에 실패하였습니다. %s',message)
        #sys.exit()

    try:
        logger.info('한글 외의 글자를 삭제합니다.')
        hangul = re.compile('[^ ㄱ-ㅣ가-힣]+')
        for j in range(len(contents)):
            if re.match('[^ ㄱ-ㅣ가-힣]+',str(contents[j])):
                no_kor_num+=1
        contents = [hangul.sub('',str(contents[cn])) for cn in range(len(contents))]
        logger.info('한글 외의 글자를 가진',no_kor_num,'개의 문서 삭제를 완료했습니다.')
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)#+"\n"+ str(trace_back)
        logger.error('한글 외의 글자 삭제에 실패하였습니다.. %s',message)
        #sys.exit()

    try:
        logger.info('각 문서의 명사를 추출합니다.')
        tokenized_doc = []
        for cnt in tqdm(range(len(contents))):
            nouns = tagger.nouns(contents[cnt])
            tokenized_doc.append(nouns)
        logger.info('각 문서의 명사추출을 완료했습니다.')
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)#+"\n"+ str(trace_back)
        logger.error('각 문서의 명사를 추출에 실패하였습니다.. %s',message)
        #sys.exit()

    # 한글자 단어들 지우기!
    try:
        logger.info('한 글자 단어를 삭제합니다.')
        num_doc = len(tokenized_doc)
        one_word=0

        for i in range(num_doc):
            tokenized_doc[i] = [word for word in tokenized_doc[i] if len(word) > 1]

        logger.info("한 글자 단어를 삭제를 완료했습니다.")
    except Exception as e:
        trace_back=traceback.format_exc()
        message=str(e)#+"\n"+ str(trace_back)
        logger.error('한 글자 단어를 삭제에 실패하였습니다.. %s',message)
        #sys.exit()
    return tokenized_doc