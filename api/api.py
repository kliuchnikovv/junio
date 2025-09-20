import uuid
import logging

from flask import request, jsonify
from service.config import ConfigLoader

class API:
    def __init__(self, app, agent, config_loader=None):
        if not app:
            raise ValueError("app can't be None")

        # Use provided config_loader or create new one
        if config_loader is None:
            config_loader = ConfigLoader()
            config_loader.load()

        # Validate API key is available
        try:
            config_loader.get_api_key()
        except ValueError as e:
            raise ValueError(str(e))

        self.app = app
        self.agent = agent
        self.config_loader = config_loader

        self.register()

        logging.debug("API created")

    def get_data(self):
        request_id = str(uuid.uuid4())

        try:
            data = request.get_json(force=True)
        except Exception as e:
            logging.error(f"JSON parsing error: {e}")
            return None, self.send_error(400, f"Invalid JSON: {str(e)}")

        if data is None:
            return None, self.send_error(400, "No JSON data provided")

        logging.info(f"got request: id: {request_id}, data: {data}")
        data['request_id'] = request_id

        return data, None

    def send(self, code, msg):
        return jsonify(msg), code

    def send_error(self, code, text):
        return self.send(code, {'error': text})

    def register(self):
        self.app.add_url_rule('/message', 'message', self.message, methods=['POST'])

    def message(self):
        data, error = self.get_data()
        if error:
            return error

        if data is None:
            return self.send_error(400, "No data provided")

        message = data.get('message')
        thread_id = data.get('thread_id')

        if not message or not thread_id:
            return self.send_error(400, 'message and thread_id are required')

        try:
            agent_final_state, error = self.agent.handle_message(message, thread_id)
            if error:
                logging.error(f"internal error: {error}")
                return self.send_error(500, f"internal error: {error}")

            # Convert messages to serializable format
            messages = agent_final_state.get("messages", []) if agent_final_state else []
            serializable_state = {
                "messages": [
                    {
                        "type": msg.__class__.__name__,
                        "content": msg.content,
                        "id": getattr(msg, 'id', None),
                        "name": getattr(msg, 'name', None)
                    }
                    for msg in messages
                ]
            }

            request_id = data.get('request_id', 'unknown')
            logging.debug(f"request processed: id {request_id}")
            return jsonify(serializable_state)
        except Exception as e:
            logging.error(f"internal error: {e}")
            return self.send_error(500, f"internal error: {e}")
