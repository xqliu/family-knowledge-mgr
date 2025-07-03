-- Initialize pgvector extension for family knowledge management system
-- This script runs automatically when the PostgreSQL container starts

-- Enable the vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension is loaded
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Set up database for optimal vector operations
ALTER DATABASE family_knowledge SET maintenance_work_mem = '512MB';