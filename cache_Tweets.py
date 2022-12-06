# %%
import requests
from requests_oauthlib import OAuth1
import os
import json
import TwitterSecrets

# %%
CACHE_FILENAME = "Twitter_cache.json"
CACHE_DICT = {}
NUM_CACHE_TWEETS = 100


# %%
bearer_token = TwitterSecrets.Bearer_Token
client_key = TwitterSecrets.API_Key
client_secret = TwitterSecrets.API_Key_Secret
access_token = TwitterSecrets.Access_Token
access_token_secret = TwitterSecrets.Access_Token_Secret

# %%
search_url = "https://api.twitter.com/2/tweets/search/recent"
query_params = {'query': '#MarchMadness'}

# %%


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

# %%


def open_cache():
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

# %%


def save_cache(cache_dict):
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


def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


# %%
class Tweet:

    def __init__(self, user_id="No ID", text="No Text", json=None):
        self.user_id = user_id
        self.text = text
        self.json = json

        if self.json != None:
            self.user_id = json['user_id']
            self.text = json['text']

    def get_tweet(self):
        return self.text


def main():
    json_response = connect_to_endpoint(search_url, query_params)
    print(json.dumps(json_response, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()

# %%
