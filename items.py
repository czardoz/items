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

import json
import heapq
import logging

from flask import Flask, request, jsonify, Response
from flask.ext.pymongo import PyMongo

from helpers import GeoLocation, calculate_distance, nested_update

app = Flask('items_db')  # DB name is picked up from this by default
mongo = PyMongo(app)
logger = logging.getLogger(__name__)


@app.route('/items/<item_id>', methods=['GET', 'PATCH'])
def item_resource(item_id):
    item = mongo.db.items.find_one({'_id': item_id})
    if not item:
        return jsonify({'message': 'Item not found: {}'.format(item_id)}), 404

    if request.method == 'PATCH':
        item_data = json.loads(request.data)  # Load even without application/json header
        item = nested_update(item, item_data)
        item['price_difference'] = item['original_price'] - item['price']
        mongo.db.items.update({'_id': item_id}, {'$set': item}, upsert=False)
    return jsonify(item)


@app.route('/items', methods=['GET'])
def items_resource():
    buffer_list = []
    all_items = mongo.db.items.find()
    for item in all_items:
        buffer_list.append(item)
    resp = Response(response=json.dumps(buffer_list), status=200, mimetype='application/json')
    return resp


@app.route('/search/nearest', methods=['GET'])
def nearest_n_items():
    distances_heap = []
    client_lat = request.args.get('lat', None)
    client_long = request.args.get('long', None)

    if client_lat is None or client_long is None:
        return jsonify({'message': 'Latitude and longitude must be specified'}), 400

    client_location = GeoLocation(client_lat, client_long)

    for item in mongo.db.items.find():
        item_location = GeoLocation(item['locality']['lat'], item['locality']['long'])
        distance = calculate_distance(client_location, item_location)
        logger.debug('Calculated distance: {} --> {}'.format(item['_id'],  distance))
        heapq.heappush(distances_heap, (distance, item))

    n = min(3, len(distances_heap))
    nsmallest = heapq.nsmallest(n, distances_heap)

    buffer_list = [item for _, item in nsmallest]
    resp = Response(response=json.dumps(buffer_list), status=200, mimetype='application/json')
    return resp


@app.route('/search/deals', methods=['GET'])
def best_n_deals():
    n = int(request.args.get('n', 0)) or 3
    deals = mongo.db.items.find().sort('price_difference', -1).limit(n)
    buffer_list = []
    for deal in deals:
        logger.debug('Found awesome deal: {} - {} discount'.format(deal['_id'], deal['price_difference']))
        buffer_list.append(deal)
    resp = Response(response=json.dumps(buffer_list), status=200, mimetype='application/json')
    return resp

if __name__ == '__main__':
    app.run()
