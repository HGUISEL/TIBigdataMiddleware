# TIB middleware
```
common
lstm
lda
raw data sample
relatedDocs
tfidf
```

## 

## common module
* 데이터 분석에 공통적으로 들어가는 기능을 담당하는 모듈
* 백엔드에 쿼리로 데이터 호출
* 데이터 전처리
* 데이터 분석 알고리즘 시간 측정
* 포함하는 모듈

 
## lda
* 주제 분석 LDA 알고리즘
* 당장 사용하지 않음
* lstm 으로 환승

## lstm
* 주제 분석 알고리즘
* lstmRunn.py 실행하면 ES에서 문서 불러와서 학습한 뒤 몽고에 저장
* ES index을 환경에 맞게 바꿔야 함

## raw data sample
* 실험용 사이즈 ES raw 데이터
* Labs에서 ES으로 보낼 수 있음
* offline에서 실험할 떄 사용
  
## relatedDoc
* rcmd.py
* 키워드 분석한 뒤 연관문서로 변환해서 몽고에 저장

## tfidf
* tfidf.py
* ES에서 문서 불러와서 키워드 모델 학습한 뒤 몽고에 저장

# common 모듈 함수 설명

### config.py : 데이터 호출과 전처리에 사용되는 global 변수 및 시간 담당 함수

## prs.py : 데이터 전처리(pre process) 기능
### data pre process function module
* function : esLoadDocs()
  * purpose : 
    * esFunc을 사용해서 쿼리를 보내 데이터를 호출
    * 서버에 연결 불가 혹은 서버 연결 옵션에 따라 저장되어 있는 sample data을 호출
    * 내용이 없는 문서를 걸러준다.
    * NOTICE :
      *  readtData에서 부르는 중간 함수이다.

* function : dataPrePrcs
  * purpose : 
    * okt을 사용해서 형태소 분석을 진행. 
* function : readyData
  * purpose : 데이터를 호출해서 부적절한 데이터를 거르고, 형태소 분석까지 완료해서 반환
  * input : int : 호출하고자 하는 문서의 수
  * output : 문서들의 (id list, title list, 형태소 분석 단어 list) tuple
  * NOTICE : id, title, 형태소 list는 동일한 index을 가지고 있다.



## esFunc.py : elasticsearch quary functions module
### elasticsearch quary functions module
* 참고 : esFunc 모듈을 만들 당시 문서의 수가 극소했음. 문서가 첨부파일을 가지고 있으면 질 좋은 문서였고, 첨부파일이 없으면 시덥잖은 문서였음. 데이터 분석 알고리즘의 정확도를 확인하기 위해 첨부파일 있는 문서와 없는 문서를 고루 섞은 데이터를 활용했음. 데이터 수가 충분하면 첨부 파일 유무에 상관 없이 불러오는 것도 문제 없을 것으로 예상 함. 기관 분류, 날짜 분류 등에 쿼리문을 변경해서 활용할 수 있을 것으로 기대


* **function : genQuery(boolean, [int])**
  * prpose : es에 보낼 쿼리를 만든다.
  * input : 
    * file 있는 문서인지 없는 문서인지 선택
    * 요청할 size 선택 : [0,infin]
  * output : es 쿼리 body(object)

* **function : esCount(object)**
  * purpose : 주어진 쿼리 바디에 해당하는 문서의 개수의 카운트를 한다.
  * input : es 쿼리 body
  * output : 문서의 개수(int)

* **function : esQueryRaw(object)**
  * purpose : 전처리를 하지 않은 데이터 반환
  * input : es 쿼리 body object
  * output : json 형태의 데이터(object)

* **function : esQuery(object)**
  * purpose : 알고리즘에 맞게 수정할 수 있도록 기본적인 전처리만 끝낸 데이터 반환
  * input : es 쿼리 body object
  * output : json 형태의 데이터(object)

* **function : nkdbNoFile(int)**
  * purpose : es에 파일이 ***없는*** 문서를 요청한 수 만큼 문서 집단을 반환
  * input : 가지고 오려는 문서의 개수(int)
  * output : (문서 object array)
            [
              {"_id" : 문서1 고유 id, "post_title" : "문서1제목","contents" : "문서1내용"},
              {"_id" : 문서2 고유 id, "post_title" : "문서2제목","contents" : "문서2내용"},
              ...
            ]  

* **function : nkdbFile(int)**
  * purpose :es에 파일이 ***있는*** 문서를 요청한 수 만큼 문서 집단을 반환
  * input : 가지고 오려는 문서의 개수(int)
  * output : (문서 object array)
            [
              {"_id" : 문서1 고유 id, "post_title" : "문서1제목","contents" : "문서1내용"},
              {"_id" : 문서2 고유 id,"post_title" : "문서2제목","contents" : "문서2내용"},
              ...
            ]  

* **function : esGetDocs(int)**
  * purpose : 첨부 파일이 있든 없든, 종류에 상관 없이 요청한 수 만큼 문서 집단을 반환
  * input : 가지고 오려는 문서의 개수(int)
  * output : (문서 object array tuple)
            [
              {"_id" : 문서1 고유 id, "post_title" : "문서1제목","contents" : "문서1내용"},
              {"_id" : 문서2 고유 id,"post_title" : "문서2제목","contents" : "문서2내용"},
              ...
            ] 
  * NOTICE : 
    * 전체 요청 수를 반으로 나눠서 파일이 있는 문서와 없는 문서에 각각 요청한다. 
    * 첨부 파일이 있는 문서와 없는 문서의 수가 다르기 때문에, 
    * 만약 한쪽에서 수가 모자라면 부족한 부분을 다른 쪽에서 채운다. 
    * 만약 전체 DB에 있는 데이터보다 많은 양을 요청하면 DB에 저장되어 있는 수만 반환.
  
* **function : esGetDocsSave([int])**
  * purpose : 첨부 파일이 있든 없든, 종류에 상관 없이 요청한 수 만큼 문서 집단을 반환해서 저장
  * input : [optional : 가지고 오려는 문서의 개수(int)]
  * NOTICE : 
    * default = 20개의 문서를 가지고 옴. 
    * 저장되는 위치는 ./raw data sample/
    * 파일 이름 : rawData.json
    * optional을 선택하면 데이터 파일 이름이 rawDataX.json으로 자동으로 저장

* **function : esGetADoc([int])**
  * purpose : es에서 random을 선택된 문서를 1개를 가지고 온다.
  * input : [optional : 가지고 오려는 "후보" 문서의 수. default size = 500]
  * output : (문서 object array)
            [
              {"post_title" : "문서 제목","contents" : "문서 내용"}
            ]  