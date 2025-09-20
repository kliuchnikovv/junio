.PHONY: help install dev server clean docker-build docker-run docker-stop test

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Create virtual environment and install dependencies"
	@echo "  dev          - Run the agent directly (python agent.py)"
	@echo "  server       - Run the Flask server (python app.py)"
	@echo "  clean        - Remove virtual environment and cache files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo "  docker-stop  - Stop and remove Docker container"
	@echo "  test         - Run tests (if available)"

# Install dependencies in virtual environment
install:
	python -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

# Run the agent directly
dev:
	. venv/bin/activate && python agent.py

# Run the Flask server
server:
	. venv/bin/activate && python app.py

# Clean up
clean:
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Docker commands
docker-build:
	docker-compose build

docker-run:
	docker-compose up

docker-stop:
	docker-compose down

# Test command (placeholder)
test:
	@echo "No tests configured yet"
	# . venv/bin/activate && python -m pytest