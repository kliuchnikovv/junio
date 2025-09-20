import os
import sys
import logging

from flask import Flask
from api.api import API

# Configure logging only once
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Handle unhandled exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print(f"Unhandled exception: {exc_type.__name__}: {exc_value}")

sys.excepthook = handle_exception

app = Flask(__name__)
port = os.getenv('PORT', 3000)
api = API(app)

if __name__ == '__main__':
    print(f"Server is running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=int(port), debug=False, use_reloader=False)
