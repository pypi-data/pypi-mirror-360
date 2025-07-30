import requests

def retrieveORCIDinfo(first_name, last_name):
    """function that retrieves ORCID relevant information
    inputs: first_name, last_name
    outputs: orcid_record"""

    orcid_info = 'NIL'
    headers = {'Content-Type': 'application/vnd.orcid+json'}
    query = 'https://pub.orcid.org/v3.0/search/?q=family-name:' + last_name+'+AND+given-names:'+first_name
    resp = requests.get(query, headers=headers)
    results = resp.json()
    try:
        # Check whether we have a match
        if results['num-found'] == 1:
            # In case of a single match retrieve the orcid id
            orcid = results['result'][0]['orcid-identifier']['path']
            r = requests.get(f'https://pub.orcid.org/v3.0/expanded-search/?start=0&rows=200&q=orcid:{orcid}',headers=headers)
            results = r.json()
            orcid_info = results['expanded-result'][0]
    except:
        orcid_info = 'NIL'

    return orcid_info