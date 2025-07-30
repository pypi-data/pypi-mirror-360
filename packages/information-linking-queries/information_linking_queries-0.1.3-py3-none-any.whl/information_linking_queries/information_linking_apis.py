from .wikipedia import retrieve_wikipedia_description, retrieve_wikipedia_label
from .wikidata import retrieve_wikidata_url, retrieve_wikidata_aliases
from .dbpedia import retrieve_dbpedia_url

def information_linking(wikipedia_url, description=True, label=True, wikidata=True, aliases=True, dbpedia=True):
    if not wikipedia_url or "curid=" not in wikipedia_url:
        raise ValueError("\nPlease provide a Wikipedia URL like: 'https://en.wikipedia.org/wiki/curid=18630637'.")
    
    outputs = {}

    if description:
      outputs["description"] = retrieve_wikipedia_description(wikipedia_url)
    if label:
      outputs["label"] = retrieve_wikipedia_label(wikipedia_url)
    if wikidata:
      outputs["wikidata"] = retrieve_wikidata_url(wikipedia_url)
    if aliases:
      outputs["aliases"] = retrieve_wikidata_aliases(wikipedia_url)
    if dbpedia:
      outputs["dbpedia"] = retrieve_dbpedia_url(wikipedia_url)

    return outputs