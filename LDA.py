import json
from common.cmm import showTime
from common.cmm import SAMP_DATA_DIR
from common import prs

# download LDA result if True
DOWNLOAD_DATA_OPTION = False 
# Frontend directory to store LDA result
from common.cmm import LDA_DIR_FE

# download LDA model if True
SAVE_LDA_MODEL = True

NUM_TOPICS = 3
NUM_ITER = 10

def DBG(whatToBbg):
    print("\n\n\n\n#####DEBUG-MODE#####")
    print(whatToBbg)
    print("#####DEBUG-MODE#####\n\n\n\n")
    return 

def runLda(titles, tokenized_doc, contents):  
    # LDA 알고리즘
    print("LDA algo 분석 중...")
    from gensim import corpora
    dictionary = corpora.Dictionary(tokenized_doc)#문서 별 각 단어에 고유 id 부여
    corpus = [dictionary.doc2bow(text) for text in tokenized_doc]# 문서를 벡터화?

    import gensim
    ldamodel = gensim.models.ldamodel.LdaModel(
        corpus, num_topics=NUM_TOPICS, id2word=dictionary, passes=NUM_ITER)
    
    # Save model to disk.
    if SAVE_LDA_MODEL == True:
        
        fileName = "c"+str(len(corpus))+"i"+str(NUM_ITER)+"t"+str(NUM_TOPICS)
        import os
        curDir = os.getcwd()
        from pathlib import Path
        fileDir = str(Path(curDir).parent)
        ldaFile = fileDir+"\\LDA_model\\"+fileName
        print("cur dir : ", fileDir)
        #save your model as 
        import dill
        with open(ldaFile,'wb') as f:
            dill.dump(ldamodel, f)
        
        #save corpus
        corpusName = "corpus"+str(len(corpus))
        corpusFile = fileDir+"\\LDA_model\\"+ corpusName
        with open(corpusFile,'wb') as f:
            dill.dump(corpus, f)
        # later load the model as
        # model = gensim.models.Doc2vec.load('file-name')

        # from gensim.test.utils import datapath
        # fileName = currDir + "corpus:"+str(len(corpus))+"_ite:"+str(NUM_ITER)+"_top:"+str(NUM_TOPICS)
        # ldaModelFile = datapath(fileName)
        # print(ldaModelFile)
        # ldamodel.save(ldaModelFile)
        # Load a potentially pretrained model from disk.
        # ldamodel = gensim.models.ldamodel.LdaModel.load(ldaFile)
# 


    # topics = ldamodel.print_topics(num_words=10)
    topics = ldamodel.show_topics(num_words=3, formatted=False)
    print("\n\nLDA 분석 완료!")
    


    print("\n\n##########LDA 분석 결과##########")
    for i, topic in topics:
        print(i,"번째 토픽을 구성하는 단어: ", topic)
    
    # topic_lkdhd : topic_likelyhood, 문서 당 최대 경향 토픽만을 산출하기
    # 같은 토픽 별로 정렬
    print()
    topic_lkdhd = []
    from operator import itemgetter
    for i, topic_list in enumerate(ldamodel[corpus]):
        # if i == 5:
            # break
        topic_list = sorted(topic_list, key=itemgetter(1), reverse = True) 
        print(i,'번째 문서의 최대 경향 순서 topic 정렬',topic_list)
        topic_lkdhd.append((i, topic_list[0][0]))
    
   # tokenized_doc에는 개별 문서들의 단어들이 tokenized되어 저장되어 있다.
    # 같은 토픽에 있는 문서들을 정리 + 문서의 제목과 함께 엮어서 pair으로 묶는다.
    """
    [
        [//새로운 토픽
            0,1,2,3,4//문서 01,2,3,4가 같은 토픽
        ],
        [
            //새로운 토픽
            5,6,7,8,9// 문서 5,6,7,8,9가 같은 토픽
        ],
        ...
    ]
    """

    topic_lkdhd = sorted(topic_lkdhd, key=itemgetter(1), reverse = True)
    num_docs = len(topic_lkdhd)
    topicIdx = -1
    sameTopicDocArrTitle = []

    for i in range(num_docs):

        docIndex = topic_lkdhd[i][0]
        # 지금 보고 있는 문서번호가 관심 있는 주제에 속한다면, 같은 토픽에 추가! topic_lkdhd = [ (문서번호, 주제), (문서 번호, 주제),...]
        # 새로운 토픽으로 이동.
        if topicIdx != (topic_lkdhd[i][1]):

            # topic_lkdhd에서 i번째 문서의 번호
            sameTopicDocArrTitle.append([{"doc": docIndex, "title": titles[docIndex], "words" : tokenized_doc[docIndex], "contents" : contents[docIndex]}])
            topicIdx = topic_lkdhd[i][1]  # 현재 관심있는 문서 번호 업데이트
        else:
            # sameTopicDocArrTitle 맨 마지막에 새로운 문서번호로 추가!
            sameTopicDocArrTitle[-1].append({"doc": docIndex, "title": titles[docIndex], "words" : tokenized_doc[docIndex], "contents" : contents[docIndex]})

    ldaResult = []
    for topicIdx, wvtArr in topics:
        arr = []
        for w,v in wvtArr:
            arr.append(w)
        ldaResult.append({"topic" : {"topic_num":topicIdx, "words" : arr}, "doc" : sameTopicDocArrTitle[topicIdx]})

    print("투입된 문서의 수 : %d\n설정된 Iteratin 수 : %d\n설정된 토픽의 수 : %d" %(num_docs, NUM_ITER, NUM_TOPICS))

    return ldaResult

################################################
"""
LDA 잠재 디리클레 할당
2019.12.27.
"""

"""
function : LDA()
purpose : 자동으로 문서들을 주제들로 분류해준다. gensim 라이브러리 사용
input : num of documents, num of iteration, num of topics
output : 주제 별로 분류된 array
[
    [
        문서1, "문서1 제목", ["문서1 단어1","문서1 단어2"],
        문서X, "문서X 제목", ["문서X 단어1","문서X 단어2"],
        문서Y, "문서Y 제목", ["문서Y 단어1","문서Y 단어2"]
    ],
    [
        문서2, "문서2 제목", ["문서2 단어1","문서2 단어2"],
        문서J, "문서J 제목", ["문서J 단어1","문서J 단어2"],
        문서K, "문서K 제목", ["문서K 단어1","문서K 단어2"]
    ],
    [
        같은 주제로 분류된 문서들...
    ],
    ...
]
"""

def LDA(ndoc, nit = NUM_ITER, ntp = NUM_TOPICS):

    # change global value if get new params.
    global NUM_ITER
    global NUM_TOPICS

    if NUM_ITER != nit:
        NUM_ITER = nit 
    if NUM_TOPICS != ntp:
        NUM_TOPICS = ntp 

    print("LDA Algo 시작!")

    print("##########Pahse 0 : LDA option:##########",
         "\nDOWNLOAD OPTION : ", str(DOWNLOAD_DATA_OPTION),
        #  "\nBACKEND CONNECTION OPTION : ", str(BACKEND_CONCT),
        #  "\nRANDOM ORDER OPTION : ", str(RANDOM_MODE)
         )


    # Phase 1 : READY DATA
    print("\n\n##########Phase 1 : READY DATA##########")
    (doc_id, titles, tokenized_doc, contents) = prs.readyData(ndoc, True)
   

    # LDA 알고리즘
    print("\n\n##########Phase 2 : LDA Algo##########")
    result = runLda(titles, tokenized_doc,contents)

    if DOWNLOAD_DATA_OPTION == True:
        with open(LDA_DIR_FE, 'w', -1, "utf-8") as f:
            json.dump(result, f, ensure_ascii=False)


    # import os
    # currDirPath = os.getcwd()
    # currDir = os.path.split(currDirPath)[1]
    # # parentDirPath = os.path.split(currDirPath)[0]
    # # parDir = os.path.split(parentDirPath)[1]
    # if currDir != "common":
    #     # try:
    #     if currDir == "TIBigdataMiddleware":
    #         os.chdir(currDirPath+"\\common")
    #         print("dir path adjusted!")
    #     else:
    #         print("dir path error! check file cmm.py")

         
    with open( "../../TIBigdataFE/src/assets/special_first/test.json", 'w', -1, "utf-8") as f:
        json.dump(result, f, ensure_ascii=False)



     # showTime()
    showTime()
    
    if DOWNLOAD_DATA_OPTION == True:
        print("Analysis Result has been stored at ",LDA_DIR_FE)
    print("LDA Analysis Fin!")
    return result