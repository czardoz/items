#!/usr/bin/env python
#
# Items - Mongo Project
#
# Copyright (C) 2015 Aniket Panse <aniketpanse@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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