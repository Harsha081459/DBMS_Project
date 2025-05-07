-- Database Schema for Global Logistics Tracking Platform
-- This script contains the structure for the MySQL database.

-- 1. Create Packages Table
CREATE TABLE IF NOT EXISTS packages (
    tracking_number VARCHAR(50) PRIMARY KEY,
    sender_name VARCHAR(100),
    receiver_name VARCHAR(100),
    weight FLOAT,
    cargo_type VARCHAR(50),
    shipping_cost FLOAT,
    status VARCHAR(50),
    current_location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create Tracking History Table (1-to-Many Relationship)
CREATE TABLE IF NOT EXISTS tracking_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tracking_number VARCHAR(50),
    status VARCHAR(50),
    location VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tracking_number) REFERENCES packages(tracking_number) ON DELETE CASCADE
);

-- Note: The Python Streamlit app automatically executes these queries 
-- on startup if the tables do not already exist.
