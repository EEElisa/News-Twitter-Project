import csv
import statistics


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


def group_accounts(lst_account_dic):
    ny = dict.fromkeys(['ny_low', 'ny_high'], [])
    dc = dict.fromkeys(['dc_low', 'dc_high'], [])
    for account_dic in lst_account_dic:
        if account_dic['Location'] == "NY":
            if account_dic['popularity'] == "low":
                ny['ny_low'].append(account_dic['Name'])
            else:
                ny['ny_high'].append(account_dic['Name'])
        else:
            if account_dic['popularity'] == "low":
                dc['dc_low'].append(account_dic['Name'])
            else:
                dc['dc_high'].append(account_dic['Name'])
    return ny, dc


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
        if type(self.val) != str:
            print(prefix + ", ".join(self.val))
        else:
            print(prefix + self.val)
        if self.children:
            for child in self.children:
                child.print_tree()
        else:
            pass


def build_account_tree(ny_accounts, dc_accounts):
    root = Node("Popular Accounts")

    ny = Node("NY")
    ny_low_pop = Node("Low Popularity")
    ny.add_child(ny_low_pop)
    ny_high_pop = Node("High Popularity")
    ny.add_child(ny_high_pop)

    ny_low_account = Node(ny_accounts['ny_low'])
    ny_low_pop.add_child(ny_low_account)
    ny_high_account = Node(ny_accounts['ny_high'])
    ny_high_pop.add_child(ny_high_account)

    dc = Node("DC")
    dc_low_pop = Node("Low Popularity")
    dc.add_child(dc_low_pop)
    dc_high_pop = Node("High Popularity")
    dc.add_child(dc_high_pop)

    dc_low_account = Node(dc_accounts['dc_low'])
    dc_low_pop.add_child(dc_low_account)
    dc_high_account = Node(dc_accounts['dc_high'])
    dc_high_pop.add_child(dc_high_account)

    root.add_child(ny)
    root.add_child(dc)

    return root


def get_twitter_username(name, lst_account_dic):
    for account in lst_account_dic:
        if account['Name'] == name:
            return account['Screen name']
        else:
            pass


if __name__ == '__main__':
    correct = ["yes", 'y', 'yup', 'sure']
    location = ["NY", "DC", "Unknown"]

    filename = "300_Twitter_accounts.csv"
    with open(filename, 'r') as f:
        dict_reader = csv.DictReader(f)
        list_of_dict = list(dict_reader)
    f.close()

    # remove empty dict
    list_of_dict = [item for item in list_of_dict if item]

    lst_account_dic = name_unknwon_loc(list_of_dict)

    # print(get_location_list(lst_account_dic))
    lst_account_dic = standardize_loc(lst_account_dic)
    print("The number of accounts in NY/DC is", len(lst_account_dic))

    lst_account_dic = eva_popularity(lst_account_dic)
    ny, dc = group_accounts(lst_account_dic)

    root = build_account_tree(ny, dc)
    root.print_tree()

    print(get_twitter_username("Ezra Klein", lst_account_dic))
