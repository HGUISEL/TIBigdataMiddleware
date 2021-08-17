import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname('TextMining/Tokenizer'))))

from numpy.core.records import array
 
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer

from TextMining.Tokenizer.kubic_morph import *
from TextMining.Tokenizer.kubic_data import *
from TextMining.Tokenizer.kubic_mystorage import *
from TextMining.Analyzer.kubic_wordCount import *

from io import StringIO
import gridfs
import csv
from collections import defaultdict

def tfidf(email, keyword, savedDate, optionList, analysisName):
    corpus = search_in_mydoc2(email, keyword, savedDate)['all_content'].tolist()    #문장으로 이루어진 doc
    nTokens = optionList
    #print("corpus\n", corpus, "\nNumber of Doc: ",len(corpus))
    top_words = getCount(email, keyword, savedDate, optionList)[0]
    top_words = json.loads(top_words)
    
    tfidf_vectorizer = TfidfVectorizer().fit(top_words)
    feature_names = tfidf_vectorizer.get_feature_names()

    df = pd.DataFrame(tfidf_vectorizer.transform(corpus).toarray(), columns=feature_names)
    words = tfidf_vectorizer.get_feature_names()
    print("Tfidf 단어사전\n",words)
    print("Tfidf 결과\n", df)    
    
    df_T = df.T.sum(axis=1)
    #df_T['word'] = words
    #df_T['rate']= df.T.sum(axis=1) #단어별 tfidf 합친 값
    #df_T = df_T[['word', 'rate']]
    
    print(df_T.index, df_T.values)

    '''
    # barchar 및 워드클라우드 mongo저장 안함.

    ## Barchart 그리기
    FONT_PATH='TextMining/NanumBarunGothic.ttf'
    fontprop = fm.FontProperties(fname=FONT_PATH, size=8)
    plt.figure(figsize=(20,5))
    plt.bar(df_T.index, df_T.values)
    plt.xticks(rotation=40, ha='right', fontproperties=fontprop)
    print("tfidf barchart 결과파일이 생성되었습니다..")
    plt.savefig('tfidf_barchart.jpg')

    ## Wordcloud 시각화
    Cloud = WordCloud(font_path = FONT_PATH,background_color="white", max_words=50).generate_from_frequencies(df_T)
    print("tfidf wordcloud 결과파일이 생성되었습니다..")
    Cloud.to_file('tfidf_wordcloud.jpg')
    
    #Mongo에 저장된 바차트, 워드클라우드의 binary 파일과 이미지파일이 일치하는지 length를 통해 확인
    from os.path import getsize
    BarFile = 'tfidf_barchart.jpg'    
    WcFile = 'tfidf_wordcloud.jpg'
    bar_file_size = getsize(BarFile)
    wc_file_size = getsize(WcFile)
    
    print('File Name: %s \tFile Size: %d' %(BarFile, bar_file_size))
    print('File Name: %s \tFile Size: %d' %(WcFile, wc_file_size))

    
    ### Mongo 저장 ### 
    client=MongoClient(host='localhost',port=27017)
    #print('MongoDB에 연결을 성공했습니다.')
    db=client.textMining
    nTokens = optionList
    now = datetime.datetime.now()
    #print("time: ", now,'\n', now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")) #형식
    
    '''

    '''
    ## 몽고db에 Barchart 이미지 binary로 저장
    print("\nMongoDB에 Tfidf 분석 결과를 바차트로 저장합니다.")
    fs = gridfs.GridFS(db, 'tfidf') #tfidf.files, tfidf.chunks로 생성됨
    with open(BarFile, 'rb') as f:
        contents = f.read()
    fs.put(contents, filename='tfidf_bar')

    ## 몽고db에 WordCloud 이미지 binary로 저장
    print("MongoDB에 Tfidf 분석 결과를 wordcloud로 저장합니다.\n")
    with open(WcFile, 'rb') as f:
        contents = f.read()
    fs.put(contents, filename='tfidf_wordcloud')

    barBinary = getBinaryImage(bar_file_size, analysisName)
    wcBinary = getBinaryImage(wc_file_size, analysisName)

    doc={
        "userEmail" : email,
        "keyword" : keyword,
        "savedDate": savedDate,
        "analysisDate" : datetime.datetime.now(),
        #"duration" : ,
        "nTokens" : nTokens,
        "resultJson" : json.dumps(dict(df_T), ensure_ascii=False),
        "resultBar" : barBinary,
        "resultWC" : wcBinary
        #"resultCSV":
    }
    db.tfidf.insert_one(doc)  

    print("MongoDB에 저장되었습니다.")
    '''
    return df

#tfidf('sujinyang@handong.edu', '북한', "2021-07-08T11:46:03.973Z", 100, 'tfidf')
#tfidf('21600280@handong.edu', '통일', "2021-07-08T11:46:03.973Z", 100, 'tfidf')
