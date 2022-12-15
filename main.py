import Secrets
from utility import *
from userTree import *
import requests
from nltk.corpus import stopwords
import re
from flask import Flask, render_template, request

app = Flask(__name__)

bearer_token = Secrets.Bearer_Token
client_key = Secrets.API_Key
client_secret = Secrets.API_Key_Secret
access_token = Secrets.Access_Token
access_token_secret = Secrets.Access_Token_Secret
NYT_keys = Secrets.NYT_key

filename = "300_Twitter_accounts.csv"
with open(filename, 'r') as f:
    dict_reader = csv.DictReader(f)
    list_of_dict = list(dict_reader)
f.close()

# preprocess the account dic
lst_account_dic = name_unknwon_loc(list_of_dict)
lst_account_dic = standardize_loc(lst_account_dic)
print("The number of accounts in NY/DC is", len(lst_account_dic))

lst_account_dic = eva_popularity(lst_account_dic)
ny, dc = group_accounts(lst_account_dic)
root = build_account_tree(ny, dc)


num_cache_tweets = 100
users_cache_filename = "userinfo_cache.json"
users_cache_dic = open_cache(users_cache_filename)
user_lookup_url = "https://api.twitter.com/2/users/by"

user_timeline_cache_filename = "user_timeline_cache.json"
user_timeline_cache_dic = open_cache(user_timeline_cache_filename)

nyt_cache_filename = "NYT_cache.json"
nyt_cache_dic = open_cache(nyt_cache_filename)
nyt_search_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r


def make_request(url, params):
    '''Make a request to the Web API using the baseurl and params
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
    '''Collect all the Tweets (text) from the given json response 
    Parameters
    ----------
    json_response: json dictionary
        The json dictionary that contains the result of the timeline search for the given account 
    Returns
    -------
    list
        the results of all searched Tweets 
    int 
        the length of the list (i.e. the number of Tweets collected)
    '''
    tweets_dic = json_response['data']
    tweets_lst = []
    for t in tweets_dic:
        text = t['text']
        tweets_lst.append(text)
    n_tweets = len(tweets_lst)
    return tweets_lst, n_tweets


def get_user_id(json_response, username):
    '''get user id on Twitter given the username 
    Parameters
    ----------
    json_response: json dictionary
        the json dictionary that contains the account information for the given username 
    username: string 
        the username of a certain Twitter account 
    Returns
    -------
    string
        the user id of the given Twitter account  
    '''
    user_info = json_response['data']
    for user in user_info:
        if user['username'] == username:
            return user['id']
        else:
            pass


def word_freq(tweets_lst, n):
    '''find the top n most popular words that occur in the Tweets 
    Parameters
    ----------
    tweets_lst: list
        a list of Tweet texts 
    n: int
        the number of popular words requested  
    Returns
    -------
    list
        the list of top n words 
    dictionary
        the dictionary of word-occurrences pair 
    '''
    stopword = stopwords.words("english")
    words_lst = []
    for tweet in tweets_lst:
        for word in tweet.split():
            word = word.lower()
            word = re.sub(r'[^\w\s]', '', word)
            if word not in stopword and len(word) > 0 and word != "rt":
                words_lst.append(word)
            else:
                pass

    word_freq_dic = dict()
    for word in words_lst:
        word_freq_dic[word] = word_freq_dic.get(word, 0) + 1
    word_freq_dic = dict(
        sorted(word_freq_dic.items(), key=lambda item: item[1], reverse=True))
    word_top_n = [list(word_freq_dic.keys())[i] for i in range(n)]
    return word_top_n, word_freq_dic


def make_request_nyt(url, params):
    '''Make a request to the NYT API using the baseurl and params
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
    CACHE_DICT: dictionary 
        The dictionary for the cache file 
    CACHE_FILENAME: string 
        The file name for caching 
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


def articles_info(json_response):
    '''extract article information from the json response loaded from json 
    Parameters
    ----------
    json_response: json dictionary
        the json dictionary that contains dictionaries of NYT articles 
    Returns
    -------
    dictionary 
        a dictionary that stores headline and url of each article  
    '''
    articles_set = json_response['response']['docs']
    articles_info = {}
    for article in articles_set:
        headline = article['headline']['main']
        url = article['web_url']
        articles_info[headline] = url
    return articles_info


@app.route('/')
def index():
    return render_template('index.html')  # just the static HTML


@app.route('/handle_form', methods=['POST'])
def account_lst():
    # get "location" and "popularity" from the user and return the corresponding account list by searching through the tree
    location = request.form["location"]
    popularity = request.form["popularity"]
    search_condition = [location, popularity]
    result = root.search_accounts(search_condition)
    n = len(result)
    return render_template('response.html', account_list=result, n=n)


@app.route('/get_tweets', methods=['POST'])
def search_tweets():
    # get "name" from user and use it to get the account's user id and the relevant Tweets using timeline searching API.
    # return the list of frequent words along with the whole dictionary to the html for display
    num_keywords = int(request.form['n_word'])
    account_idx = int(request.form['twitter_account'])
    account_name = lst_account_dic[account_idx]['Name']
    account = lst_account_dic[account_idx]['Screen name']
    user_query_para = {"usernames": account, "user.fields": "id"}
    user_info_json = make_request_with_cache(
        user_lookup_url, user_query_para, users_cache_dic, users_cache_filename)

    user_id = get_user_id(user_info_json, account)
    user_timeline_url = "https://api.twitter.com/2/users/{}/tweets".format(
        user_id)
    timeline_query_para = {"tweet.fields": "text",
                           "max_results": num_cache_tweets}
    user_timeline_json = make_request_with_cache(
        user_timeline_url, timeline_query_para, user_timeline_cache_dic, user_timeline_cache_filename)
    user_tweets, n_tweets = get_tweets(user_timeline_json)  # a list of Tweets
    word_top_n, word_freq_dic = word_freq(user_tweets, n=num_keywords)
    return render_template('freq_words.html', account=account_name, n_tweets=n_tweets, word_list=word_top_n, word_dic=word_freq_dic, n_words=num_keywords)


@app.route('/get_nyt', methods=['POST'])
def search_nyt():
    # get search query (i.e. "keyword") from the user to search relevant NYT articles
    # return the headlines and urls to url for display
    search_query = request.form['keyword']
    NUM_REQUESTED = int(request.form['quantity'])
    PAGE_NUM = NUM_REQUESTED // 10
    pages = []  # lst of page number, each page contains 10 results
    for i in range(PAGE_NUM):
        pages.append(str(i+1))
    headlines = []
    urls = []
    articles_dic = {}
    for page in pages:
        query_params = {'title': search_query,
                        'document_type': "article", 'page': page, 'sort': 'relevance', 'api-key': NYT_keys}
        nyt_articles = make_request_nyt_with_cache(
            nyt_search_url, query_params, nyt_cache_dic, nyt_cache_filename)
        articles = articles_info(nyt_articles)
        headlines.extend(list(articles.keys()))
        urls.extend(list(articles.values()))
        articles_dic.update(articles)
    n_articles = len(headlines)
    return render_template("search_nyt.html", headlines=headlines, uels=urls, articles_dic=articles_dic, n=n_articles, query=search_query)


if __name__ == "__main__":
    app.run(debug=True)
