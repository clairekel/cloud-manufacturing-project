import unittest
from unittest.mock import patch
from app import app
from google.cloud import firestore
from google.api_core import exceptions as firestore_exceptions

class TestCloudManufacturing(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # Basic functionality tests
    def test_existing_product(self):
        """Test response for an existing product."""
        response = self.app.post('/check_product', json={'ProductName': 'keychain'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Product is ready to manufacture')

    def test_non_existing_product(self):
        """Test response for a non-existing product."""
        response = self.app.post('/check_product', json={'ProductName': 'doesntexist'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Product is not available')

    def test_case_insensitivity(self):
        """Test case insensitivity of product names."""
        response = self.app.post('/check_product', json={'ProductName': 'KEYCHAIN'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Product is ready to manufacture')

    # Input validation tests
    def test_invalid_request(self):
        """Test response for an invalid request (empty JSON)."""
        response = self.app.post('/check_product', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

    def test_invalid_json(self):
        """Test response for invalid JSON input."""
        response = self.app.post('/check_product', data='invalid json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid JSON', response.get_json()['error'])

    def test_missing_product_name(self):
        """Test response when product name is missing."""
        response = self.app.post('/check_product', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid request', response.get_json()['error'])

    def test_empty_product_name(self):
        """Test response for empty product name."""
        response = self.app.post('/check_product', json={'ProductName': ''})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'You left the product field blank. Please try enter the product again.')

    def test_whitespace_product_name(self):
        """Test response for whitespace-only product name."""
        response = self.app.post('/check_product', json={'ProductName': '   '})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'You left the product field blank. Please try enter the product again.')

    def test_special_characters(self):
        """Test handling of special characters in product name."""
        response = self.app.post('/check_product', json={'ProductName': 'product!@#$%^&*()'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Product is not available')

    def test_very_long_product_name(self):
        """Test handling of very long product names."""
        long_name = 'a' * 1000
        response = self.app.post('/check_product', json={'ProductName': long_name})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Product is not available')

    # HTTP method tests
    def test_options_request(self):
        """Test CORS headers on OPTIONS request."""
        response = self.app.options('/check_product')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertIn('Access-Control-Allow-Headers', response.headers)
        self.assertIn('Access-Control-Allow-Methods', response.headers)

    def test_non_post_method(self):
        """Test response for non-POST methods."""
        response = self.app.get('/check_product')
        self.assertEqual(response.status_code, 405) 

    # Error handling tests
    def test_database_error(self):
        """Test handling of general database errors."""
        with patch('routes.firestore.Client', side_effect=Exception('Database connection error')):
            response = self.app.post('/check_product', json={'ProductName': 'keychain'})
            self.assertEqual(response.status_code, 400)
            data = response.get_json()
            self.assertIn('error', data)
            self.assertEqual(data['error'], 'Database error occurred')

    def test_firestore_timeout(self):
        """Test handling of Firestore timeout errors."""
        with patch('routes.firestore.Client', side_effect=firestore_exceptions.DeadlineExceeded('Timeout')):
            response = self.app.post('/check_product', json={'ProductName': 'keychain'})
            self.assertEqual(response.status_code, 400)
            data = response.get_json()
            self.assertIn('error', data)
            self.assertEqual(data['error'], 'Database error occurred')

if __name__ == '__main__':
    unittest.main()