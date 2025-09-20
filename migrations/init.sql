-- Database initialization script for LangGraph
-- This script sets up the initial database structure

-- Create extension for UUID generation (if needed)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant all privileges on the database to the postgres user
GRANT ALL PRIVILEGES ON DATABASE langgraph TO postgres;

-- Note: LangGraph PostgresSaver will create its own tables automatically
-- This script just ensures the database is properly set up

-- Create a simple health check table for monitoring
CREATE TABLE IF NOT EXISTS health_check (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(50) NOT NULL DEFAULT 'langgraph',
    status VARCHAR(20) NOT NULL DEFAULT 'healthy',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial health check record
INSERT INTO health_check (service_name, status)
VALUES ('langgraph', 'initialized')
ON CONFLICT DO NOTHING;