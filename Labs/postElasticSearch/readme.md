# postES.py
## what to
* save raw sample data from ES to use search data in local development

## how to
* run elasticsearch in local with port 9200(default port)
* make sure there is rawrawData.json file in middleware/raw sample data/
* run python3 postES.py
* check if the data is saved in ES using bash
```
    curl -XGET "localhost:9200/nkdb/_search"
```