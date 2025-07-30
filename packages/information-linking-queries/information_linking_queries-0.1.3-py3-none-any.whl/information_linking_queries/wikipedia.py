import requests
from .helpers import cleaner

def retrieve_wikipedia_description(url):
    id = url.split("=")[-1].strip()
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&pageids={id}&exintro=&exsentences=2&explaintext=&redirects=&formatversion=2&format=json"
    json_data = requests.get(url).json()
    cleaned_first_sents = cleaner(json_data.get('query', {}).get('pages', [{}])[0].get('extract', 'NIL'))
    return cleaned_first_sents

def retrieve_wikipedia_label(url):
    id = url.split("=")[-1].strip()
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&pageids={id}&exintro=&exsentences=2&explaintext=&redirects=&formatversion=2&format=json"
    json_data = requests.get(url).json()
    title = cleaner(json_data.get('query', {}).get('pages', [{}])[0].get('title', 'NIL'))
    return title