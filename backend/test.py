import os
import json
import unittest
from unittest.mock import patch, MagicMock
from app import app
from google.cloud import firestore
from google.api_core import exceptions as firestore_exceptions
from google.oauth2.service_account import Credentials
from google.cloud import secretmanager
from dotenv import load_dotenv

load_dotenv(override=False)

print("Environment variables in test.py:")
for key, value in os.environ.items():
    print(f"{key}: {value}")

project_id = os.environ.get('PROJECT_ID')
secret_id = os.environ.get('SECRET_ID')
firestore_secret = os.environ.get('FIRESTORE_SECRET')

print(f"PROJECT_ID: {project_id}")
print(f"SECRET_ID: {secret_id}")
print(f"FIRESTORE_SECRET: {firestore_secret}")

def access_secret(project_id, secret_id, version_id="latest"):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    try:
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode('UTF-8')
    except Exception as e:
        print(f"Error accessing secret: {e}")
        return None

# Use the firestore_secret directly, no need to access it again
if firestore_secret:
    print("Successfully retrieved Firestore secret from environment")
else:
    print("Failed to retrieve Firestore secret from environment")

# Parse the secret value (assuming it's a JSON string)
# Parse the secret and create credentials
credentials = Credentials.from_service_account_info(json.loads(secret_value))

# Use the credentials as needed
# For example, to create a Firestore client:
db = firestore.Client(credentials=credentials)

class TestCloudManufacturing(unittest.TestCase):

    def setUp(self):
        load_dotenv()  # This loads the variables from .env
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