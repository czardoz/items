import json
import heapq

from flask import Flask, request, jsonify, Response
from flask.ext.pymongo import PyMongo

from helpers import GeoLocation, calculate_distance

app = Flask('items_db')  # DB name is picked up from this by default
app.debug = True
mongo = PyMongo(app)


@app.route('/items/<item_id>', methods=['GET', 'PATCH'])
def item_resource(item_id):
    item = mongo.db.items.find_one({'_id': item_id})
    if not item:
        return jsonify({'message': 'Item not found: {}'.format(item_id)}), 404

    if request.method == 'PATCH':
        item_data = json.loads(request.data)  # Load even without application/json header
        item.update(item_data)
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
    client_location = GeoLocation(client_lat, client_long)

    if not client_lat or not client_long:
        return jsonify({'message': 'Latitude and longitude must be specified'}), 400

    for item in mongo.db.items.find():
        item_location = GeoLocation(item['locality']['lat'], item['locality']['long'])
        distance = calculate_distance(client_location, item_location)
        heapq.heappush(distances_heap, (distance, item))
    n = min(10, len(distances_heap))
    nsmallest = heapq.nsmallest(n, distances_heap)
    resp = Response(response=json.dumps(nsmallest), status=200, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run()
