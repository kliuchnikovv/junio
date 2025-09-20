import os
import sys
import logging

from flask import Flask
from api.api import API
from service.checkpointer import CheckpointerFactory
from service.agent.agent import chat_agent
from langchain_google_genai import ChatGoogleGenerativeAI

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

app   = Flask(__name__)
port  = os.getenv('PORT', 3000)
debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'

# Create checkpointer using factory
checkpointer = CheckpointerFactory.create(debug_mode)
checkpointer_type = CheckpointerFactory.get_checkpointer_type()

agent = chat_agent(
    ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        debug_mode=debug_mode,
    ), 
    [], 
    checkpointer,
)

api   = API(app, agent)

if __name__ == '__main__':
    logging.info(f"Server is running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=int(port), debug=False, use_reloader=False)
