from common import prs
ndoc = 100
prsResult = prs.readyData(ndoc,True)
import pandas as pd
d = pd.DataFrame(list(prsResult))
d.columns
