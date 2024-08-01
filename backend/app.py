from flask import Flask
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

# Import routes after creating the app
from routes import check_product

# Register the route
app.add_url_rule('/check_product', 'check_product', check_product, methods=['POST', 'OPTIONS'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)