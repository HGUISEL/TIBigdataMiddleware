import json
with open('./latest_prs_result.json', 'r') as f:
    data = json.load(f)


#content의 수가 더 많다. prs가 잘 안된듯? 문서 내용이 없는 것도 있고, 한글자 단위로 토큰이 쪼개진 문서들은 또 중간에 제외해서 엉망이다... prs 함수 다듬어야 함.
data_ = {"id" : data["idList"], "titles" : data["titles"], "token" : data["tokenized_doc"]}



import pandas as pd
df = pd.DataFrame.from_dict(data_)
print(len(df))
#Nan 확인. nan 데이터는 없다. 문제는... 
df.isnull().any
df_token = df.drop(df[df["token"].map(len) < 1].index)
df_token = df_token.reset_index(drop=True)
#token column에 길이가 0인 list도 있음. 그래서 다음 단계인 join에서 에러가 난다.
#print(type(data))

for i in range(len(df_token)):
    #df_token.iloc[i,"token"] = " ".json(df["token"][i])
    df_token.loc[i,"token"] = " ".join(df_token["token"][i])
#print(df_token.head(3))


