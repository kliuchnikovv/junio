import os
import logging

from flask import request, jsonify

class API:
    def __init__(self, app, agent):
        if not app:
            raise ValueError("app can't be None")

        # Check for required environment variables
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        self.app = app
        self.agent = agent

        self.register()

        logging.debug("API created")

    def get_data(self):
        try:
            data = request.get_json()
        except Exception as e:
            return None, self.send_error(400, f"Invalid JSON: {e}")

        logging.info(f"got request: {data}")
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
            return self.send_error(400, "Invalid JSON")

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
            serializable_state = {
                "messages": [
                    {
                        "type": msg.__class__.__name__,
                        "content": msg.content,
                        "id": getattr(msg, 'id', None),
                        "name": getattr(msg, 'name', None)
                    }
                    for msg in agent_final_state.get("messages", [])
                ]
            }

            logging.debug(f"request processed: {serializable_state}")
            return jsonify(serializable_state)
        except Exception as e:
            logging.error(f"internal error: {e}")
            return self.send_error(500, f"internal error: {e}")
