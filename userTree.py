import csv
import statistics

filename = "300_Twitter_accounts.csv"
with open(filename, 'r') as f:
    dict_reader = csv.DictReader(f)
    list_of_dict = list(dict_reader)
f.close()

correct = ["yes", 'y', 'yup', 'sure']
location = ["NY", "DC", "Unknown"]


# remove empty dict
list_of_dict = [item for item in list_of_dict if item]


def name_unknwon_loc(lst_account_dict):
    for dic in lst_account_dict:
        if len(dic['Location']) == 0:
            dic['Location'] = "Unknown"
    return lst_account_dict


def get_location_list(lst_account_dict):
    location_lst = [dict['Location'] for dict in lst_account_dict]
    result = {}
    for loc in location_lst:
        if loc not in result.keys():
            result[loc] = 1
        else:
            result[loc] += 1
    sorted_result = {k: v for k, v in sorted(
        result.items(), key=lambda item: item[1])}
    return sorted_result


def standardize_loc(lst_account_dic):
    ny_lst = ["New York, NY", "New York", "New York City",
              "NYC", "brooklyn", "new york", "Brooklyn"]

    dc_lst = ["Washington, DC", "Washing, D.C.",
              "Washington", "Washington D.C.", "DC"]

    result_lst = []
    for account in lst_account_dic:
        if account['Location'] in ny_lst:
            account['Location'] = "NY"
            result_lst.append(account)
        elif account['Location'] in dc_lst:
            account['Location'] = "DC"
            result_lst.append(account)
    return result_lst


lst_account_dic = name_unknwon_loc(list_of_dict)

# print(get_location_list(lst_account_dic))
lst_account_dic = standardize_loc(lst_account_dic)
print("The number of accounts in NY/DC is", len(lst_account_dic))


# divide the accounts into two parts - low vs. high popularity
def eva_popularity(lst_account_dic):
    follower_lst = [dic["All followers"] for dic in lst_account_dic]
    median_pop = statistics.median([int(i) for i in follower_lst])
    # print("median populatiry is", median_pop)
    for account in lst_account_dic:
        if int(account['All followers']) <= median_pop:
            account['popularity'] = 'low'
        else:
            account['popularity'] = 'high'
    return lst_account_dic


lst_account_dic = eva_popularity(lst_account_dic)

# high_pop = 0
# low_pop = 0
# for dic in lst_account_dic:
#     if dic['popularity'] == 'high':
#         high_pop += 1
#     else:
#         low_pop += 1
# print(high_pop)
# print(low_pop)


class Account():
    def __init__(self, account=None, name=None, all_followers=None, nyt_followers=None, location=None, bio=None, popularity=None):
        self.account = account
        self.name = name
        self.all_followers = all_followers
        self.nyt_followers = nyt_followers
        self.location = location
        self.bio = bio
        self.popularity = None


class Node():
    def __init__(self, val):
        self.val = val
        self.children = []
        self.parent = None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def get_level(self):
        level = 0
        p = self.parent
        while p:
            level += 1
            p = p.parent
        return level

    def print_tree(self):
        spaces = ' ' * self.get_level() * 2
        prefix = spaces + "|__" if self.parent else ""
        print(prefix + self.val)
        if self.children:
            for child in self.children:
                child.print_tree()

    def traverse(self, prefix='', bend=''):
        print(f'{prefix}{bend}{self.account}')
        if self.left:
            if bend == '+-':
                prefix = prefix + '| '
            elif bend == '`-':
                prefix = prefix + '  '
            self.left.traverse(prefix, bend="+-")


def build_account_tree():
    root = Node("Popular Accounts")

    ny = Node("NY")
    ny.add_child(Node("Low Popularity"))
    ny.add_child(Node("High Popularity"))

    dc = Node("DC")
    dc.add_child(Node("Low Popularity"))
    dc.add_child(Node("High Popularity"))

    root.add_child(ny)
    root.add_child(dc)

    return root


if __name__ == '__main__':
    root = build_account_tree()
    root.print_tree()
