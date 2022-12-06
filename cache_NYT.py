import requests
import os
import json
import Secrets
from utility import *

NYT_keys = Secrets.NYT_key


def make_request_nyt(url, params):
    response = requests.get(url, params=params)
    return response.json()


def make_request_nyt_with_cache(baseurl, params, CACHE_DICT, CACHE_FILENAME):
    '''Check the cache for a saved result for this baseurl+params
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs
    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    request_key = construct_unique_key(baseurl, params)
    if request_key in CACHE_DICT.keys():
        print("cache hit!", request_key)
        json_response = CACHE_DICT[request_key]
        return json_response
    else:
        print("cache miss!", request_key)
        CACHE_DICT[request_key] = make_request_nyt(baseurl, params)
        save_cache(CACHE_DICT, CACHE_FILENAME)
        json_response = CACHE_DICT[request_key]
        return json_response


def main():
    # %%
    CACHE_FILENAME = "NYT_cache.json"
    CACHE_DICT = open_cache(CACHE_FILENAME)

    base_url_nyt = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    query = "thanksgiving"

    page = ['1', '2', '3', '4', '5'] # each page contains 10 results 
    query_params = {'title': query,
                    'document_type': "article", 'page': '2', 'sort': 'relevance', 'api-key': NYT_keys}

    nyt_articles = make_request_nyt_with_cache(
        base_url_nyt, query_params, CACHE_DICT, CACHE_FILENAME)

    print(len(nyt_articles['response']['docs']))


if __name__ == "__main__":
    main()
