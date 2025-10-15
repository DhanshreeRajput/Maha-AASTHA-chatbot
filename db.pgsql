-- Create database
CREATE DATABASE maha_aastha;

-- Connect to the database
-- \c maha_aastha_grievancess;

-- Create grievancess table
CREATE TABLE grievancess (
    id SERIAL PRIMARY KEY,
    ticket VARCHAR(50) UNIQUE NOT NULL,
    employee_id VARCHAR(50) NOT NULL,
    employee_name VARCHAR(255) NOT NULL,
    mobile_number VARCHAR(15) NOT NULL,
    designation VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    office_name VARCHAR(255) NOT NULL,
    district_name VARCHAR(255) NOT NULL,
    official_email VARCHAR(255) NOT NULL,
    user_role VARCHAR(100) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    issue_timestamp TIMESTAMP,
    issue_category VARCHAR(100) NOT NULL,
    issue_sub_category VARCHAR(100) NOT NULL,
    issue_related VARCHAR(100) NOT NULL,
    issue_section VARCHAR(100),
    issue_sub_section VARCHAR(100),
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Open',
    files_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_grievancess_mobile_number ON grievancess(mobile_number);
CREATE INDEX idx_grievancess_ticket ON grievancess(ticket);
CREATE INDEX idx_grievancess_employee_id ON grievancess(employee_id);
CREATE INDEX idx_grievancess_status ON grievancess(status);
CREATE INDEX idx_grievancess_created_at ON grievancess(created_at);