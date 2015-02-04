#!/usr/bin/env python

import argparse
import json

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

if __name__ == '__main__':

    client = MongoClient('mongodb://localhost:27017/')
    db = client['items_db']
    items = db.items

    print items.find_one({'_id': 'item1'})