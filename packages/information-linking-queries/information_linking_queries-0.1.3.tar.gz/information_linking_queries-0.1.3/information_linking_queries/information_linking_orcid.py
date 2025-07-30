from .orcid import retrieveORCIDinfo

def information_linking_orcid(first_name, last_name):
    if not first_name or not last_name:
        raise ValueError("\nPlease provide a first name and a last name")
    else:
        orcid = retrieveORCIDinfo(first_name, last_name)

    return orcid