#!/usr/bin/env python

import argparse
import json

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help='Path to input JSON file.')
    args = parser.parse_args()

    client = MongoClient('mongodb://localhost:27017/')
    db = client['items_db']
    items = db.items

    with open(args.infile, 'r') as datafile:
        data = json.load(datafile)
        for item in data:
            item_id = item['_id']
            item['price_difference'] = item['original_price'] - item['price']
            print 'Inserting item: {}'.format(item_id)
            items.update({'_id': item_id}, {'$set': item}, upsert=True)


    print 'Insertion complete.'
    print 'Current items:'
    for i in items.find():
        print i['_id']