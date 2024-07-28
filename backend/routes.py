from flask import request, jsonify
from google.cloud import firestore
import json
import logging

def check_product():
    print("Received request")
    logging.debug(f"Received request: {request.method}")
    logging.debug(f"Request headers: {dict(request.headers)}")
    logging.debug(f"Raw request data: {request.get_data(as_text=True)}")
    
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "POST":
        try:
            raw_data = request.get_data(as_text=True)
            print(f"Attempting to parse JSON: {raw_data}")
            request_json = json.loads(raw_data)
            print(f"Parsed JSON: {request_json}")
            
            if not request_json or 'ProductName' not in request_json:
                return jsonify({'error': 'Invalid request'}), 400

            product_name = request_json['ProductName'].strip().lower()
            if not product_name:
                return jsonify({'message': 'Product is not available'}), 200
            
            print(f"Product name: {product_name}")

            try:
                db = firestore.Client()
                doc_ref = db.collection('products').document(product_name)
                doc = doc_ref.get()
                
                if doc.exists:
                    message = 'Product is ready to manufacture'
                else:
                    message = 'Product is not available'
            except Exception as e:
                print(f"Firestore error: {str(e)}")
                return jsonify({'error': 'Database error'}), 500  # Return 500 error

            return jsonify({'message': message}), 200
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {str(e)}")
            return jsonify({'error': f'Invalid JSON: {str(e)}'}), 400
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'error': str(e)}), 400

def _build_cors_preflight_response():
    response = jsonify({})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response