import json
import random
import string
import items
import unittest

from pymongo import MongoClient


class ItemsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = items.app.test_client()
        self.mongoclient = MongoClient('mongodb://localhost:27017/')
        self.db = self.mongoclient['items_db']
        self.populate_db()

    def tearDown(self):
        self.db.drop_collection('items')

    def test_update_nonexistant_item(self):
        updated_data = {
            "createdAt": "2014-11-03T13:35:07.290Z",
            "description": "Test Item 1",
            "locality": {
                "lat": 13.094454,
                "long": 77.586012
            },
            "name": "Test Item 1",
            "pics": [
                "test_pic_1",
                "test_pic_2"
            ],
            "price": 9500,
            "original_price": 1200,
            "purchase_year": 2010
        }

        resp = self.app.patch('/items/asd', data=json.dumps(updated_data))

        self.assertEquals(resp.status, '404 NOT FOUND')

    def test_update_item(self):

        updated_desc = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
        updated_long = random.uniform(77.4, 77.6)

        updated_data = {
            "createdAt": "2014-11-03T13:35:07.290Z",
            "description": updated_desc,
            "locality": {
                "lat": 13.094454,
                "long": updated_long
            },
            "name": "Test Item 1",
            "pics": [
                "test_pic_1",
                "test_pic_2"
            ],
            "price": 9500,
            "original_price": 1200,
            "purchase_year": 2010
        }

        resp = self.app.patch('/items/item1', data=json.dumps(updated_data))
        self.assertEquals(resp.status, '200 OK')

        # send a get for the same item, and process the response
        resp = self.app.get('/items/item1')
        updated_item = json.loads(resp.data)
        self.assertEquals(updated_item['description'], updated_desc)
        self.assertEquals(updated_item['locality']['long'], updated_long)  # Makes sure nested values are updated

    def test_get_all_items(self):
        expected_number_of_items = self.db.items.count()
        resp = self.app.get('/items')
        actual_number_of_items = len(json.loads(resp.data))
        self.assertEquals(expected_number_of_items, actual_number_of_items)

    def test_nearest_items_no_lat_provided(self):
        resp = self.app.get('/search/nearest')
        response_data = json.loads(resp.data)
        self.assertEquals(response_data['message'], 'Latitude and longitude must be specified')

    def test_nearest_items(self):
        resp = self.app.get('/search/nearest?lat=22.1&long=55.6')
        actual_items = json.loads(resp.data)
        expected_items = ['item9', 'item10', 'item11']
        for expected_item in expected_items:
            present = False
            for actual_item in actual_items:
                if actual_item['_id'] == expected_item:
                    present = True
                    break
            self.assertTrue(present)

    def test_best_deals_no_param(self):
        resp = self.app.get('/search/deals')

        actual_items = json.loads(resp.data)
        expected_items = ['item9', 'item10', 'item5']

        self.assertEquals(len(actual_items), len(expected_items))
        for expected_item in expected_items:
            present = False
            for actual_item in actual_items:
                if actual_item['_id'] == expected_item:
                    present = True
                    break
            self.assertTrue(present)

    def test_best_deals_with_param(self):
        resp = self.app.get('/search/deals?n=2')
        actual_items = json.loads(resp.data)
        expected_items = ['item9', 'item10']

        self.assertEquals(len(actual_items), len(expected_items))

        for expected_item in expected_items:
            present = False
            for actual_item in actual_items:
                if actual_item['_id'] == expected_item:
                    present = True
                    break
            self.assertTrue(present)

    def populate_db(self):
        items_ = self.db.items
        with open('data.json', 'r') as datafile:  # Autoclose file
            data = json.load(datafile)
            for item in data:
                item_id = item['_id']
                item['price_difference'] = item['original_price'] - item['price']
                items_.update({'_id': item_id}, {'$set': item}, upsert=True)

if __name__ == '__main__':
    unittest.main()