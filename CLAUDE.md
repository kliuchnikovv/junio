# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a Python LangGraph agent project that implements a conversational AI using Google's Gemini model. The project uses Flask server with LangChain Python.

The implementation creates a React agent using LangGraph's `create_react_agent` with:
- Google Gemini 2.0 Flash model for language understanding
- MemorySaver for conversation persistence
- Empty tools array (ready for extension)
- Thread-based conversation management

## Development Commands

### Python Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the Python agent directly
python agent.py

# Run the Flask server
python app.py
```

### Docker Development
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Configuration

The application uses a YAML-based configuration system with environment variable overrides:

- **Configuration File**: `config.yaml` (copy from `config.template.yaml`)
- **Environment Variables**: `.env` file for sensitive data (API keys, passwords)
- **Override Support**: Environment variables override YAML settings

### Configuration Structure
- `app`: Application settings (name, version, debug, port)
- `model`: LLM configuration (provider, model name, parameters)
- `checkpoint`: Database/persistence settings (auto/memory/postgres)
- `api`: API endpoints and CORS settings
- `tools`: Available tools configuration (extensible)
- `logging`: Logging level and format
- `graph`: Graph node configuration

### API Endpoints
- `/message` - POST endpoint for chat messages (accepts `message` and `thread_id`)
- `/health` - GET endpoint for health checks (configurable)

## Code Structure

- `agent.py`: Core agent creation and configuration
- `app.py`: Flask HTTP server implementation with `/invoke` endpoint
- Error handling implemented for unhandled exceptions
- Message serialization for JSON responses

## Key Dependencies

- langgraph: LangGraph framework
- langchain-google-genai: Gemini model integration
- flask: HTTP server
- python-dotenv: Environment variable loading
