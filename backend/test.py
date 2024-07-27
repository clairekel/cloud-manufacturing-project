import os
import unittest
from app import app, db

# Ensure we're in the testing environment
os.environ['FLASK_ENV'] = 'testing'

class TestCloudManufacturing(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True 
        self.db = db

    def test_existing_product(self):
        # Add a test product to Firestore
        self.db.collection('products').document('keychain').set({'name': 'keychain'})
        
        try:
            response = self.app.post('/check_product', json={'ProductName': 'keychain'})
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['message'], 'Product is ready to manufacture')
        finally:
            # Clean up: delete the test product
            self.db.collection('products').document('keychain').delete()

    def test_non_existing_product(self):
        response = self.app.post('/check_product', json={'ProductName': 'doesntexist'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Product is not available')

    def test_invalid_request(self):
        response = self.app.post('/check_product', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

    def test_options_request(self):
        response = self.app.options('/check_product')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertIn('Access-Control-Allow-Headers', response.headers)
        self.assertIn('Access-Control-Allow-Methods', response.headers)

    def test_invalid_json(self):
        response = self.app.post('/check_product', data='invalid json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid JSON', response.get_json()['error'])

    def test_missing_product_name(self):
        response = self.app.post('/check_product', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid request', response.get_json()['error'])

    def test_product_exists(self):
        # Add a test product to Firestore
        self.db.collection('products').document('existing_product').set({'name': 'existing_product'})
        
        try:
            response = self.app.post('/check_product', json={'ProductName': 'existing_product'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()['message'], 'Product is ready to manufacture')
        finally:
            # Clean up: delete the test product
            self.db.collection('products').document('existing_product').delete()

    def test_product_not_exists(self):
        non_existing_product = 'non_existing_product'
        response = self.app.post('/check_product', json={'ProductName': non_existing_product})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['message'], 'Product is not available')

    def tearDown(self):
        # Clean up any resources if necessary
        pass

if __name__ == '__main__':
    unittest.main()