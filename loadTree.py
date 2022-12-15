import csv
import statistics
from utility import *
from userTree import *

if __name__ == "__main__":
    root_loaded = loadTree("tree.json")
    root_loaded.print_tree()
