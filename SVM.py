import pandas as pd
import numpy as np

data = prs.readyData(ndoc, True)

# 중복데이터 제거
data = data.drop_duplicates()

# 모델 생성
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib
"""
text_clf_svm = Pipeline([('vect', CountVectorizer()),#'어떤 함수인지 표기'#있을때, 없을때 표로.. 차이가 없으면 리포트./왜 이게 필요한지/
                         ('tfidf', TfidfTransformer()),#tfidf(특정 단어가 특정문서에서 얼마나 중요한지 가중치를 나타내주는 계산법)
                                                       # tfidf로 count matrix를 정규화시킨다. 
                         ('clf-svm', SGDClassifier(loss='hinge', penalty='l2', alpha=0.00001, random_state=42,n_iter_no_change=5))])

#모델 학습
text_clf_svm = text_clf_svm.fit(train["키워드"], train["주제"])

#파이프라인 저장
joblib.dump(text_clf_svm,'/home/dapi2/TIBigdataMiddleware/SVM.h5')
"""
#파이프라인 불러오기
pipe=joblib.load('/home/dapi2/TIBigdataMiddleware/SVM.h5')

#모델을 이용하여 예측
predicted_svm=pipe.predict(test["contents"])##column 이름 바꾸기

print(redicted_svm)


"""
import numpy as np
test_pred = pd.DataFrame()
test_pred['index'] = test["index"]
test_pred['주제'] = test["주제"]
test_pred['예측'] = predicted_svm
test_pred

ans_count = pd.pivot_table(test_pred, columns=['주제', '예측'], aggfunc=len)
ans_count = pd.DataFrame(ans_count)
ans_count
"""