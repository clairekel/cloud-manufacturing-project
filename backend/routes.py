from flask import request, jsonify
from google.cloud import firestore
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Main function to check if a product is available for manufacturing.
# Handles both OPTIONS and POST requests.
    
def check_product():
    logger.debug(f"Received request: {request.method}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    logger.debug(f"Raw request data: {request.get_data(as_text=True)}")
    
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "POST":
        return _handle_post_request()
    else:
        return jsonify({'error': 'Method not allowed'}), 405

#Handles the POST request for product checking.
def _handle_post_request():
    try:
        request_json = _parse_json_request()
        product_name = _extract_product_name(request_json)
        message = _check_product_availability(product_name)
        return jsonify({'message': message}), 200
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

# Parses the JSON request data.
def _parse_json_request():
    
    try:
        raw_data = request.get_data(as_text=True)
        logger.debug(f"Attempting to parse JSON: {raw_data}")
        request_json = json.loads(raw_data)
        logger.debug(f"Parsed JSON: {request_json}")
        return request_json
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {str(e)}")
        raise ValueError(f'Invalid JSON: {str(e)}')

#Extracts and validates the product name from the request JSON.
def _extract_product_name(request_json):
    if not request_json or 'ProductName' not in request_json:
        raise ValueError('Invalid request: ProductName is required')

    product_name = request_json['ProductName'].strip().lower()
    if not product_name:
        raise ValueError('Product name cannot be empty')
    
    logger.debug(f"Product name: {product_name}")
    return product_name

#Checks the availability of the product in Firestore.
def _check_product_availability(product_name):
    try:
        db = firestore.Client()
        doc_ref = db.collection('products').document(product_name)
        doc = doc_ref.get()
        
        return 'Product is ready to manufacture' if doc.exists else 'Product is not available'
    except Exception as e:
        logger.error(f"Firestore error: {str(e)}")
        raise ValueError('Database error occurred')

#Builds a CORS preflight response.
def _build_cors_preflight_response(): 
    response = jsonify({})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response
