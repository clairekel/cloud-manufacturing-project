import os
import unittest
from unittest.mock import patch, MagicMock
from app import app
from google.cloud import firestore
from google.api_core import exceptions as firestore_exceptions

# Ensure we're in the testing environment
os.environ['FLASK_ENV'] = 'testing'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\clair\Downloads\cloud-based-manufacturing-32d80efcb584.json'

class TestCloudManufacturing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Replace with your test project ID
        cls.db = firestore.Client()

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_existing_product(self):
        response = self.app.post('/check_product', json={'ProductName': 'keychain'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Product is ready to manufacture')

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

    # New test cases

    def test_empty_product_name(self):
        response = self.app.post('/check_product', json={'ProductName': ''})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Product is not available')

    def test_whitespace_product_name(self):
        response = self.app.post('/check_product', json={'ProductName': '   '})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Product is not available')

    def test_case_insensitivity(self):
        response = self.app.post('/check_product', json={'ProductName': 'KEYCHAIN'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Product is ready to manufacture')

    def test_special_characters(self):
        response = self.app.post('/check_product', json={'ProductName': 'product!@#$%^&*()'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Product is not available')

    def test_very_long_product_name(self):
        long_name = 'a' * 1000
        response = self.app.post('/check_product', json={'ProductName': long_name})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Product is not available')

    @patch('routes.firestore.Client')
    def test_database_error(self, mock_firestore):
        mock_firestore.side_effect = Exception('Database connection error')
        response = self.app.post('/check_product', json={'ProductName': 'keychain'})
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Database error')

    def test_non_post_method(self):
        response = self.app.get('/check_product')
        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    @patch('routes.firestore.Client')
    def test_firestore_timeout(self, mock_firestore):
        mock_firestore.side_effect = firestore_exceptions.DeadlineExceeded('Timeout')
        response = self.app.post('/check_product', json={'ProductName': 'keychain'})
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Database error')

    def tearDown(self):
        # Clean up any resources if necessary
        pass

if __name__ == '__main__':
    unittest.main()