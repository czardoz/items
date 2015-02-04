import json
import random
import string
import items
import unittest


class ItemsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = items.app.test_client()

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

        updated_data = {
            "createdAt": "2014-11-03T13:35:07.290Z",
            "description": updated_desc,
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

        resp = self.app.patch('/items/item1', data=json.dumps(updated_data))
        self.assertEquals(resp.status, '200 OK')

        # send a get for the same item, and process the response
        resp = self.app.get('/items/item1')
        updated_item = json.loads(resp.data)
        self.assertEquals(updated_item['description'], updated_desc)

if __name__ == '__main__':
    unittest.main()