import requests
from .helpers import get_results

def retrieve_wikidata_url(url):
    id = url.split("=")[-1].strip()
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&pageids={id}&formatversion=2&format=json"
    json_data = requests.get(url).json()
    wikidata_qid = json_data.get('query', {}).get('pages', [{}])[0].get('pageprops', "NIL").get("wikibase_item", "NIL")
    wikidata_url = f"https://www.wikidata.org/wiki/{wikidata_qid.strip()}"
    return wikidata_url

def retrieve_wikidata_aliases(url):
    id = url.split("=")[-1].strip()
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&pageids={id}&formatversion=2&format=json"
    json_data = requests.get(url).json()
    wikidata_qid = json_data.get('query', {}).get('pages', [{}])[0].get('pageprops', {}).get("wikibase_item", "NIL")
    if wikidata_qid != "NIL":
        alias_list = []
        query_alias = f"""SELECT ?alias
            WHERE {{
                wd:{wikidata_qid} skos:altLabel ?alias
                FILTER(LANG(?alias) = "en")
                }}
                """
        results = get_results(query_alias, "https://query.wikidata.org/sparql")
        for result in results["results"]["bindings"]:
            for key, value in result.items():
                alias = value.get("value", "NIL")
                alias_list.append(alias)
    else:
        alias_list = []
    return alias_list