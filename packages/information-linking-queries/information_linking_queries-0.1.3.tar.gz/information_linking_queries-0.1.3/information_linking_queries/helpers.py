import re
import sys
from SPARQLWrapper import SPARQLWrapper, JSON

def cleaner(text):
  text = text.replace('\\', '').replace('\n', ' ')
  text = re.sub(r'\{.*?\}', '', text)
  text = re.sub(' +', ' ', text).strip()
  return text

def get_results(query, endpoint):
  user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
  sparql = SPARQLWrapper(endpoint, agent=user_agent)
  sparql.setQuery(query)
  sparql.setReturnFormat(JSON)
  return sparql.query().convert()