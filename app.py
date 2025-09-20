import sys
import logging

from flask import Flask
from api.api import API
from service.config import ConfigLoader
from service.checkpointer import CheckpointerFactory
from service.agent.agent import chat_agent
from langchain_google_genai import ChatGoogleGenerativeAI


def setup_logging(config):
    """Setup logging based on configuration"""
    if logging.getLogger().handlers:
        return  # Already configured

    level = getattr(logging, config.logging.level.upper())
    format_str = config.logging.format

    if config.logging.file:
        logging.basicConfig(
            level=level,
            format=format_str,
            filename=config.logging.file
        )
    else:
        logging.basicConfig(
            level=level,
            format=format_str
        )


def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle unhandled exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error(f"Unhandled exception: {exc_type.__name__}: {exc_value}")


def create_app():
    """Application factory"""
    # Load configuration
    config_loader = ConfigLoader()
    config = config_loader.load()

    # Setup logging
    setup_logging(config)

    # Setup exception handling
    sys.excepthook = handle_exception

    # Create Flask app
    app = Flask(config.app.name)

    # Create checkpointer
    checkpointer = CheckpointerFactory.create(config)
    checkpointer_type = CheckpointerFactory.get_checkpointer_type(config)
    logging.info(f"Initialized with {checkpointer_type}")

    # Create agent
    agent = chat_agent(
        ChatGoogleGenerativeAI(
            model=config.model.name,
            **config.model.parameters
        ),
        config.tools.enabled,
        checkpointer,
    )

    # Create API
    api = API(app, agent, config_loader)

    logging.info(f"Application '{config.app.name}' v{config.app.version} initialized")
    return app, config


# Create the application
app, config = create_app()

if __name__ == '__main__':
    logging.info(f"Server is running on http://localhost:{config.app.port}")
    app.run(host='0.0.0.0', port=config.app.port, debug=config.app.debug, use_reloader=False)
