from .helpers import get_results

def retrieve_dbpedia_url(url):
    id = url.split("=")[-1].strip()
    dbpedia_url = "NIL"
    try:
        query_dbpedia_url = f"""SELECT ?url
            WHERE {{
                ?url dbo:wikiPageID {int(id)} .
                }}
                """
        results = get_results(query_dbpedia_url, "https://dbpedia.org/sparql/")
        for result in results["results"]["bindings"]:
            for key, value in result.items():
                dbpedia_url = value.get("value", "NIL")
    except:
        pass
    return dbpedia_url