# %%
import requests
from requests_oauthlib import OAuth1
import os
import json
import TwitterSecrets
from datetime import datetime, timezone


# %%
bearer_token = TwitterSecrets.Bearer_Token
client_key = TwitterSecrets.API_Key
client_secret = TwitterSecrets.API_Key_Secret
access_token = TwitterSecrets.Access_Token
access_token_secret = TwitterSecrets.Access_Token_Secret

# %%


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

# %%


def open_cache(CACHE_FILENAME):
    ''' opens the cache file if it exists and loads the JSON into
    a dictionary, which it then returns.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    None
    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict, CACHE_FILENAME):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME, "w")
    fw.write(dumped_json_cache)
    fw.close()


# %%


def make_request(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an API request by its baseurl and params
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs
    Returns
    -------
    string
        the unique key as a string
    '''
    param_strings = []
    connector = '_'
    for k in params.keys():
        param_strings.append(f'{k}_{params[k]}')
    param_strings.sort()
    unique_key = baseurl + connector + connector.join(param_strings)
    return unique_key


def make_request_with_cache(baseurl, params, CACHE_DICT, CACHE_FILENAME):
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
        tweets_dic = json_response['data']
        tweets_lst = []
        for t in tweets_dic:
            user_id = t['id']
            text = t['text']
            tweet = Tweet(user_id, text)
            tweets_lst.append(tweet)
        return tweets_lst
    else:
        print("cache miss!", request_key)
        CACHE_DICT[request_key] = make_request(baseurl, params)
        save_cache(CACHE_DICT, CACHE_FILENAME)
        json_response = CACHE_DICT[request_key]
        tweets_dic = json_response['data']
        tweets_lst = []
        for t in tweets_dic:
            tweet_id = t['id']
            text = t['text']
            tweet = Tweet(tweet_id, text)
            tweets_lst.append(tweet)
        return tweets_lst


# %%
class Tweet:

    def __init__(self, tweet_id="No ID", text="No Text", json=None):
        self.tweet_id = tweet_id
        self.text = text
        self.json = json

        if self.json != None:
            self.tweet_id = json['tweet_id']
            self.text = json['text']

    def get_tweet(self):
        return self.text


def main():
    # %%
    CACHE_FILENAME = "Twitter_cache.json"
    CACHE_DICT = open_cache(CACHE_FILENAME)

    NUM_CACHE_TWEETS = 100
    QUERY_TEST_LST = ["#blackfriday", "#thanksgiving"]
    search_url = "https://api.twitter.com/2/tweets/search/recent"

    for query in QUERY_TEST_LST:
        SEARCH_QUERY = query
        query_params = {'query': SEARCH_QUERY, "max_results": NUM_CACHE_TWEETS}
        tweets = make_request_with_cache(
            search_url, query_params, CACHE_DICT, CACHE_FILENAME)
        print("First 10 Tweets using the query: ", SEARCH_QUERY)
        for i in range(10):
            print(tweets[i].text)
        print(" ")


if __name__ == "__main__":
    main()
