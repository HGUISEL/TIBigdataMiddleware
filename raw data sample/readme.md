* 서버에서 기본적인 정제만 해서 가져온 raw data.

* 서버에 접속이 안될 때 사용. 

* rawDataX.json에서 X는 문서의 개수. 틀릴 수도 있으니 불러와서 array 개수 check을 해보는 것을 권장. 

* 형식
```
[
    {"post_title" : "문서1제목","contents" : "문서1내용"},
    {"post_title" : "문서2제목","contents" : "문서2내용"},
    ...
]
```

* 새로 저장하기
```
import esFunc
esFunc.esGetDocsSave(NUM_OF_DOCS) # raw data sample으로 NUM_OF_DOCS만큼 데이터 저장
```