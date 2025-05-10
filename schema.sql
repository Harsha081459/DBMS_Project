-- =================================================================================
-- Enterprise Supply Chain DBMS Schema & Seeding Script
-- Database: MySQL (Local)
-- =================================================================================

CREATE DATABASE IF NOT EXISTS logistics_db;
USE logistics_db;

-- =================================================================================
-- 1. DROP EXISTING TABLES (Reverse Dependency Order)
-- =================================================================================
DROP TABLE IF EXISTS tracking_logs;
DROP TABLE IF EXISTS shipments;
DROP TABLE IF EXISTS fleet;
DROP TABLE IF EXISTS hubs;
DROP TABLE IF EXISTS users;

-- =================================================================================
-- 2. CREATE TABLES
-- =================================================================================

-- USERS TABLE (Role-Based Access Control)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role ENUM('Admin', 'Manager', 'Customer') DEFAULT 'Customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- HUBS TABLE (Warehouses / Distribution Centers)
CREATE TABLE hubs (
    hub_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    storage_capacity_kg FLOAT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- FLEET TABLE (Trucks, Planes, Ships)
CREATE TABLE fleet (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_type ENUM('Truck', 'Cargo Plane', 'Freighter Ship') NOT NULL,
    capacity_kg FLOAT NOT NULL,
    current_hub_id INT,
    status ENUM('Available', 'In Transit', 'Maintenance') DEFAULT 'Available',
    FOREIGN KEY (current_hub_id) REFERENCES hubs(hub_id) ON DELETE SET NULL
);

-- SHIPMENTS TABLE (Core Business Entity)
CREATE TABLE shipments (
    shipment_id VARCHAR(50) PRIMARY KEY,
    customer_id INT,
    origin_hub_id INT,
    dest_hub_id INT,
    weight_kg FLOAT NOT NULL,
    cargo_type VARCHAR(50) NOT NULL,
    status ENUM('Manifested', 'In Transit', 'Out for Delivery', 'Delivered', 'Delayed') DEFAULT 'Manifested',
    shipping_cost FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (origin_hub_id) REFERENCES hubs(hub_id) ON DELETE RESTRICT,
    FOREIGN KEY (dest_hub_id) REFERENCES hubs(hub_id) ON DELETE RESTRICT
);

-- TRACKING LOGS TABLE (Audit Trail)
CREATE TABLE tracking_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    shipment_id VARCHAR(50) NOT NULL,
    hub_id INT,
    action VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id) ON DELETE CASCADE,
    FOREIGN KEY (hub_id) REFERENCES hubs(hub_id) ON DELETE SET NULL
);

-- =================================================================================
-- 3. CREATE SQL VIEWS (Advanced DBMS Feature)
-- =================================================================================

-- View for Analytics: Total Active Shipments per Hub
CREATE OR REPLACE VIEW active_hub_loads AS
SELECT 
    h.name AS hub_name, 
    h.city, 
    COUNT(s.shipment_id) AS total_active_shipments,
    SUM(s.weight_kg) AS total_weight_kg
FROM hubs h
LEFT JOIN shipments s ON h.hub_id = s.origin_hub_id 
WHERE s.status IN ('Manifested', 'In Transit', 'Delayed')
GROUP BY h.hub_id;

-- =================================================================================
-- 4. SEED DUMMY DATA
-- =================================================================================

-- Insert Users
INSERT INTO users (name, email, role) VALUES 
('System Admin', 'admin@logistics.com', 'Admin'),
('Frankfurt Manager', 'manager_fra@logistics.com', 'Manager'),
('Acme Corp', 'shipping@acme.com', 'Customer'),
('Global Tech', 'supply@globaltech.com', 'Customer');

-- Insert Hubs
INSERT INTO hubs (name, city, storage_capacity_kg) VALUES 
('JFK MegaHub', 'New York', 50000.0),
('FRA Central Depot', 'Frankfurt', 75000.0),
('SIN Asia Hub', 'Singapore', 100000.0),
('LHR Gateway', 'London', 45000.0);

-- Insert Fleet
INSERT INTO fleet (vehicle_type, capacity_kg, current_hub_id, status) VALUES 
('Cargo Plane', 15000.0, 1, 'Available'),
('Cargo Plane', 15000.0, 3, 'In Transit'),
('Truck', 5000.0, 2, 'Available'),
('Truck', 5000.0, 4, 'Maintenance'),
('Freighter Ship', 500000.0, 3, 'Available');

-- Insert Shipments
INSERT INTO shipments (shipment_id, customer_id, origin_hub_id, dest_hub_id, weight_kg, cargo_type, status, shipping_cost) VALUES 
('SHP-998877', 3, 1, 4, 150.5, 'Electronics', 'In Transit', 750.00),
('SHP-112233', 4, 3, 2, 500.0, 'Semiconductors', 'Manifested', 2500.00),
('SHP-554433', 3, 2, 1, 1000.0, 'Machinery', 'Delivered', 4500.00);

-- Insert Tracking Logs
INSERT INTO tracking_logs (shipment_id, hub_id, action, timestamp) VALUES 
('SHP-998877', 1, 'Received at Origin Hub', DATE_SUB(NOW(), INTERVAL 2 DAY)),
('SHP-998877', 1, 'Loaded onto Flight A330', DATE_SUB(NOW(), INTERVAL 1 DAY)),
('SHP-554433', 2, 'Received at Origin Hub', DATE_SUB(NOW(), INTERVAL 5 DAY)),
('SHP-554433', 1, 'Arrived at Destination Hub', DATE_SUB(NOW(), INTERVAL 2 DAY)),
('SHP-554433', NULL, 'Delivered to Customer', DATE_SUB(NOW(), INTERVAL 1 DAY)),
('SHP-112233', 3, 'Manifest Created by Customer', NOW());
