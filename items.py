import json

from flask import Flask, request, jsonify
from flask.ext.pymongo import PyMongo

app = Flask('items_db')
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
def items():
    pass

if __name__ == '__main__':
    app.run()
