import Secrets
from utility import *
from userTree import *
import requests
from requests_oauthlib import OAuth1
import os
import json
import nltk
from nltk.corpus import stopwords
import re
from operator import itemgetter
import networkx as nx
from networkx.algorithms import community

bearer_token = Secrets.Bearer_Token
client_key = Secrets.API_Key
client_secret = Secrets.API_Key_Secret
access_token = Secrets.Access_Token
access_token_secret = Secrets.Access_Token_Secret

NYT_keys = Secrets.NYT_key


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r


def make_request(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


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
        return json_response
    else:
        print("cache miss!", request_key)
        CACHE_DICT[request_key] = make_request(baseurl, params)
        save_cache(CACHE_DICT, CACHE_FILENAME)
        json_response = CACHE_DICT[request_key]
        return json_response


def get_tweets(json_response):
    tweets_dic = json_response['data']
    tweets_lst = []
    for t in tweets_dic:
        text = t['text']
        tweets_lst.append(text)
    return tweets_lst


def get_user_id(json_response, username):
    user_info = json_response['data']
    for user in user_info:
        if user['username'] == username:
            return user['id']
        else:
            pass


def word_freq(tweets_lst, n):
    stopword = stopwords.words("english")
    words_lst = []
    for tweet in tweets_lst:
        for word in tweet.split():
            word = word.lower()
            word = re.sub(r'[^\w\s]', '', word)
            if word not in stopword and len(word) > 0:
                words_lst.append(word)
            else:
                pass

    word_freq_dic = dict()
    for word in words_lst:
        word_freq_dic[word] = word_freq_dic.get(word, 0) + 1
    word_freq_dic = dict(
        sorted(word_freq_dic.items(), key=lambda item: item[1], reverse=True))
    word_top_n = [list(word_freq_dic.keys())[i] for i in range(n)]
    return word_top_n


def nodes_edges(username, wordlist):
    node_names = wordlist.append(username)
    edges = []
    for word in wordlist:
        edges.append(set(username, word))
    return node_names, edges


def build_graph(nodes, edges):
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)


class TwitterUser:
    def __init__(self, user_id="No ID", username="No User Name", name="No Name", tweets="No Tweets", top_words="No Words", json=None):
        self.user_id = user_id
        self.username = username
        self.name = name
        self.tweets = tweets
        self.top_words = top_words
        self.json = json


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


def articles_headline(json_response):
    articles_set = json_response['response']['docs']
    headlines = []
    for article in articles_set:
        headlines.append(article['headline']['main'])
    return headlines


def main():
    # TWEETS_CACHE_FILENAME = "Twitter_cache.json"
    # TWEETS_CACHE_DICT = open_cache(TWEETS_CACHE_FILENAME)

    NUM_CACHE_TWEETS = 100

    # the input is returned by get_twitter_username
    input_username = "nytimes"
    users_cache_filename = "userinfo_cache.json"
    users_cache_dic = open_cache(users_cache_filename)
    user_lookup_url = "https://api.twitter.com/2/users/by"
    user_query_para = {"usernames": input_username, "user.fields": "id"}
    user_info_json = make_request_with_cache(
        user_lookup_url, user_query_para, users_cache_dic, users_cache_filename)

    user_id = get_user_id(user_info_json, input_username)
    user_timeline_cache_filename = "user_timeline_cache.json"
    user_timeline_cache_dic = open_cache(user_timeline_cache_filename)
    user_timeline_url = "https://api.twitter.com/2/users/{}/tweets".format(
        user_id)
    timeline_query_para = {"tweet.fields": "text",
                           "max_results": NUM_CACHE_TWEETS}
    user_timeline_json = make_request_with_cache(
        user_timeline_url, timeline_query_para, user_timeline_cache_dic, user_timeline_cache_filename)
    user_tweets = get_tweets(user_timeline_json)  # a list of Tweets
    word_top_n = word_freq(user_tweets, n=10)

    print(word_top_n)
    node_names, edges = nodes_edges(input_username, word_top_n)

    # print(user_timeline_json['data'][0].keys())
    # print(get_user_id(user_info_json, "nytimes"))

    CACHE_FILENAME = "NYT_cache.json"
    CACHE_DICT = open_cache(CACHE_FILENAME)

    NUM_REQUESTED = 10
    PAGE_NUM = NUM_REQUESTED // 10
    pages = []  # lst of page number, each page contains 10 results
    for i in range(PAGE_NUM):
        pages.append(str(i+1))

    base_url_nyt = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    query = "thanksgiving"

    for page in pages:
        query_params = {'title': query,
                        'document_type': "article", 'page': page, 'sort': 'relevance', 'api-key': NYT_keys}
        nyt_articles = make_request_nyt_with_cache(
            base_url_nyt, query_params, CACHE_DICT, CACHE_FILENAME)

    headlines = articles_headline(nyt_articles)
    print(" ")
    print("Printing the headlines of relevant articles...")
    i = 1
    for headline in headlines:
        print(str(i) + ". "+headline)
        i += 1


if __name__ == "__main__":
    main()
