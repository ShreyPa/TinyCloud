-- Development database

CREATE TABLE IF NOT EXISTS apps (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'stopped',
    container_id VARCHAR(64),

    CONSTRAINT valid_status
        CHECK (status IN ('running', 'stopped'))
);

CREATE UNIQUE INDEX IF NOT EXISTS apps_name_lower_idx
ON apps (LOWER(name));


-- Create test database

CREATE DATABASE tinycloud_test;

\connect tinycloud_test


-- Test database schema

CREATE TABLE IF NOT EXISTS apps (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'stopped',
    container_id VARCHAR(64),

    CONSTRAINT valid_status
        CHECK (status IN ('running', 'stopped'))
);

CREATE UNIQUE INDEX IF NOT EXISTS apps_name_lower_idx
ON apps (LOWER(name));