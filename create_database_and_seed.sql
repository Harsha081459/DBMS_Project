-- =================================================================================
-- MySQL Script to Create Database, Tables, and Insert Sample Logistics Data
-- =================================================================================

-- 1. Create the Database (If running locally or on a server where you have full root access)
-- Note: TiDB Serverless usually provisions a default 'test' database for you. 
-- You can change 'logistics_db' to 'test' if you are running this directly on TiDB Serverless.
CREATE DATABASE IF NOT EXISTS logistics_db;
USE logistics_db;

-- =================================================================================
-- 2. Table Definitions
-- =================================================================================

-- Drop tables if they already exist to start fresh (useful for testing)
DROP TABLE IF EXISTS tracking_history;
DROP TABLE IF EXISTS packages;

-- Create Packages Table (Master Table)
CREATE TABLE packages (
    tracking_number VARCHAR(50) PRIMARY KEY,
    sender_name VARCHAR(100) NOT NULL,
    receiver_name VARCHAR(100) NOT NULL,
    weight FLOAT NOT NULL,
    cargo_type VARCHAR(50) NOT NULL,
    shipping_cost FLOAT NOT NULL,
    status VARCHAR(50) NOT NULL,
    current_location VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Tracking History Table (Detail Table with 1-to-Many Foreign Key)
CREATE TABLE tracking_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tracking_number VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    location VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tracking_number) REFERENCES packages(tracking_number) ON DELETE CASCADE
);

-- =================================================================================
-- 3. Insert Sample Seed Data
-- =================================================================================

-- Insert sample packages
INSERT INTO packages 
(tracking_number, sender_name, receiver_name, weight, cargo_type, shipping_cost, status, current_location) 
VALUES 
('TRK-98A7B6C5', 'Tech Supplies Inc.', 'John Doe', 12.5, 'Electronics', 62.50, 'In Transit', 'Frankfurt Hub'),
('TRK-44X3Y2Z1', 'Fresh Foods Co.', 'Jane Smith', 5.0, 'Perishable', 30.00, 'Out for Delivery', 'New York City'),
('TRK-11Q2W3E4', 'Global Chemicals Ltd.', 'Industrial Corp', 200.0, 'Hazardous', 1500.00, 'Manifested', 'Shanghai Port'),
('TRK-77M8N9B0', 'Amazon Warehouse', 'Alice Johnson', 2.0, 'Standard', 10.00, 'Delivered', 'London');

-- Insert historical tracking data for TRK-98A7B6C5 (Electronics)
INSERT INTO tracking_history (tracking_number, status, location, timestamp) VALUES 
('TRK-98A7B6C5', 'Manifested', 'Shenzhen Factory', DATE_SUB(NOW(), INTERVAL 3 DAY)),
('TRK-98A7B6C5', 'In Transit', 'Hong Kong Airport', DATE_SUB(NOW(), INTERVAL 2 DAY)),
('TRK-98A7B6C5', 'In Transit', 'Frankfurt Hub', DATE_SUB(NOW(), INTERVAL 1 DAY));

-- Insert historical tracking data for TRK-44X3Y2Z1 (Perishable)
INSERT INTO tracking_history (tracking_number, status, location, timestamp) VALUES 
('TRK-44X3Y2Z1', 'Manifested', 'Miami Farms', DATE_SUB(NOW(), INTERVAL 12 HOUR)),
('TRK-44X3Y2Z1', 'In Transit', 'Atlanta Hub', DATE_SUB(NOW(), INTERVAL 6 HOUR)),
('TRK-44X3Y2Z1', 'Out for Delivery', 'New York City', DATE_SUB(NOW(), INTERVAL 1 HOUR));

-- Insert historical tracking data for TRK-11Q2W3E4 (Hazardous)
INSERT INTO tracking_history (tracking_number, status, location, timestamp) VALUES 
('TRK-11Q2W3E4', 'Manifested', 'Shanghai Port', NOW());

-- Insert historical tracking data for TRK-77M8N9B0 (Standard - Delivered)
INSERT INTO tracking_history (tracking_number, status, location, timestamp) VALUES 
('TRK-77M8N9B0', 'Manifested', 'Manchester Depot', DATE_SUB(NOW(), INTERVAL 5 DAY)),
('TRK-77M8N9B0', 'In Transit', 'London Hub', DATE_SUB(NOW(), INTERVAL 3 DAY)),
('TRK-77M8N9B0', 'Out for Delivery', 'London', DATE_SUB(NOW(), INTERVAL 2 DAY)),
('TRK-77M8N9B0', 'Delivered', 'London', DATE_SUB(NOW(), INTERVAL 1 DAY));

-- =================================================================================
-- 4. Sample Queries (For testing purposes)
-- =================================================================================

-- Query to view all packages currently "In Transit"
-- SELECT * FROM packages WHERE status = 'In Transit';

-- Query to view the full tracking timeline for a specific package joined with package details
-- SELECT p.tracking_number, p.cargo_type, th.status, th.location, th.timestamp 
-- FROM packages p 
-- JOIN tracking_history th ON p.tracking_number = th.tracking_number 
-- WHERE p.tracking_number = 'TRK-98A7B6C5'
-- ORDER BY th.timestamp DESC;
