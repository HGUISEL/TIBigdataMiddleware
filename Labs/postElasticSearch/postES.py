import requests
import json

FILE_DIR = "../../raw data sample/rawData620.json"

with open(FILE_DIR,'r', encoding="utf-8") as fp:
    esData = json.load(fp)

# print(type(esData))
# print(len(esData))
print(len(esData[0]))
print(type(esData[0]))
print(esData[0].keys())
# for att in esData[0]:
    # print(att)

url = "localhost:9200/nkdb/_bulk"
body = """


       """