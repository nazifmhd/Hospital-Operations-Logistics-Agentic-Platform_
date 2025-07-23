-- PostgreSQL Database Setup Script for Multi-Agent Hospital System
-- Run this script to create the database and user

-- Connect to PostgreSQL as superuser (postgres)
-- psql -U postgres

-- Create database for the multi-agent hospital system
CREATE DATABASE multi_agent_hospital;

-- Create a dedicated user for the application
CREATE USER hospital_admin WITH PASSWORD 'hospital123';

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON DATABASE multi_agent_hospital TO hospital_admin;

-- Connect to the new database
\c multi_agent_hospital;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO hospital_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hospital_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hospital_admin;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO hospital_admin;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO hospital_admin;

-- Show connection info
SELECT current_database(), current_user;

\echo 'Database setup completed successfully!'
\echo 'Database: multi_agent_hospital'
\echo 'User: hospital_admin'
\echo 'Password: hospital123'
