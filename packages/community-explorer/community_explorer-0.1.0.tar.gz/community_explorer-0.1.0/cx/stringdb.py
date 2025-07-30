#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests


STRING_API_URL = "http://string-db.org/api"


def get_interactions(genes, required_score=900):
    output_format = "json"
    method = "network"

    ## contruct params dictionary

    params = {
        "identifiers": "\r".join(genes), # your protein list
        "species": 9606, # species NCBI identifier 
        "limit": 1, # only one (best) identifier per input protein
        "echo_query": 1, # see your input identifiers in the output
        "caller_identity": "DPS_INSA", # your app name
        "required_score": required_score,
    }

    ## contruct method URL

    request_url = "/".join([STRING_API_URL, output_format, method])

    ## Call STRING

    try:
        response = requests.post(request_url, params=params)
    except requests.exceptions.RequestException as e:
        print(e)

    ## Read and parse the results

    #data = [line.split("\t") for line in response.text.strip().split("\n")]
    
    data = pd.DataFrame.from_dict(response.json())

    data = data[data.preferredName_A.isin(genes) & data.preferredName_B.isin(genes)]

    return data
