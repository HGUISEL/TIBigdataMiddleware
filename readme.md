# flask Architecture
app.py<br>
    ----esFunc.py<br>
    ----LDA.py<br>

## app.py
* flask main app

## esFunc.py
### elasticsearch quary functions module

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
              {"post_title" : "문서1제목","contents" : "문서1내용"},
              {"post_title" : "문서2제목","contents" : "문서2내용"},
              ...
            ]  

* **function : nkdbFile(int)**
  * purpose :es에 파일이 ***있는*** 문서를 요청한 수 만큼 문서 집단을 반환
  * input : 가지고 오려는 문서의 개수(int)
  * output : (문서 object array)
            [
              {"post_title" : "문서1제목","contents" : "문서1내용"},
              {"post_title" : "문서2제목","contents" : "문서2내용"},
              ...
            ]  

* **function : esGetDocs(int)**
  * purpose : 첨부 파일이 있든 없든, 종류에 상관 없이 요청한 수 만큼 문서 집단을 반환
  * input : 가지고 오려는 문서의 개수(int)
  * output : (문서 object array)
            [
              {"post_title" : "문서1제목","contents" : "문서1내용"},
              {"post_title" : "문서2제목","contents" : "문서2내용"},
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