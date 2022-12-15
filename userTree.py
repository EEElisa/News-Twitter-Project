import csv
import statistics
from utility import *


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
    median_pop = int(statistics.median([int(i) for i in follower_lst]))
    for account in lst_account_dic:
        followers = int(account['All followers'])
        if followers <= median_pop:
            account['popularity'] = 'low'
        else:
            account['popularity'] = 'high'
    return lst_account_dic


def group_accounts(lst_account_dic):
    ny = {}
    ny['ny_low'] = []
    ny['ny_high'] = []

    dc = {}
    dc['dc_low'] = []
    dc['dc_high'] = []

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

    def isLeaf(tree):
        '''check if a tree is a leaf

        Parameters
        ----------
        tree: Node 
            a tree object

        Returns
        -------
        boolean
            True if the tree is a leaf, False if the tree is not a leaf
        '''
        return not tree.children

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

    def search_accounts(self, conditions):
        loc = conditions[0]
        pop = conditions[1]
        if loc == "NY":
            ny = self.children[0]
            if pop == "low":
                return ny.children[0].children[0].val
            else:
                return ny.children[1].children[0].val
        else:
            dc = self.children[1]
            if pop == "low":
                return dc.children[0].children[0].val
            else:
                return dc.children[1].children[0].val


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


def saveTree(tree, treeFile):
    tree_dic = {}
    root = tree.val
    tree_dic[root] = {}
    for location in tree.children:
        tree_dic[root][location.val] = {}
        for pop in location.children:
            pop_cate = pop.val
            accounts = pop.children[0].val
            tree_dic[root][location.val][pop_cate] = accounts
    save_cache(tree_dic, treeFile)


def loadTree(treeFile):
    '''load a tree from a file

    Parameters
    ----------

    treeFile: file handle
        a file handle where we are going to load the tree from

    Returns
    -------
    None or Node object 

    '''
    tree_dic = open_cache(treeFile)
    root_val = list(tree_dic.keys())[0]
    root = Node(root_val)
    for location in tree_dic[root_val].keys():
        loc_node = Node(location)
        root.add_child(loc_node)
        for pop_cate in tree_dic[root_val][location]:
            pop_node = Node(pop_cate)
            loc_node.add_child(pop_node)
            accounts = Node(tree_dic[root_val][location][pop_cate])
            pop_node.add_child(accounts)
    return root


if __name__ == "__main__":
    filename = "300_Twitter_accounts.csv"
    with open(filename, 'r') as f:
        dict_reader = csv.DictReader(f)
        list_of_dict = list(dict_reader)

    # preprocess the account dic
    lst_account_dic = name_unknwon_loc(list_of_dict)
    lst_account_dic = standardize_loc(lst_account_dic)
    print("The number of accounts in NY/DC is", len(lst_account_dic))

    lst_account_dic = eva_popularity(lst_account_dic)
    ny, dc = group_accounts(lst_account_dic)
    root = build_account_tree(ny, dc)
    saveTree(root, "tree.json")

    root_loaded = loadTree("tree.json")
    root_loaded.print_tree()
