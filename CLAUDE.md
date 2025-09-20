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

- **Environment Variables**: Uses `.env` file for configuration (API keys, PORT)
- **Port**: Server runs on port specified by `PORT` environment variable (defaults to 3000)
- **API Endpoint**: Server exposes `/invoke` POST endpoint that accepts `message` and `thread_id`

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
