import csv
import json
import os

from . import SequentialDatabase, SequentialItemset, Itemset

# location of this file is required to load resource urls
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


# helper functions
def _get_path(filename: str) -> str:
    return os.path.join(__location__, 'resources', filename)


# datasets
def load_website_tracking():
    with open(_get_path('website_tracking.csv'), 'r') as file:
        csv_reader = csv.reader(file)
        return SequentialDatabase(
            *(
                (i, SequentialItemset(*row))
                for i, row in enumerate(csv_reader, start=1)
            )
        )


def load_website_tracking2():
    with open(_get_path('website_tracking2.json'), 'r') as file:
        data = json.load(file)

        return SequentialDatabase(
            *(
                (i, SequentialItemset(*(
                    Itemset(*el)
                    for el in row
                )))
                for i, row in enumerate(data, start=1)
            )
        )


tweets_12_2020_25k_tsv_path = _get_path('tweets_12_2020_25k.tsv')
drinks_csv_path = _get_path('drinks.csv')
