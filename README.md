# Enterprise Supply Chain DBMS (Local CLI)

A robust, terminal-based database application representing a highly normalized Enterprise Supply Chain system. This project demonstrates raw backend engineering by utilizing complex SQL queries (Joins, Aggregations, Views, Foreign Key Constraints) directly from Python.

## Tech Stack
- **Database:** Local MySQL
- **Backend / Connector:** Python (`mysql-connector-python`)
- **UI:** Terminal CLI (`tabulate`)

## Features
- **5-Table Normalized Schema**: Includes role-based access control, distributed warehouses (hubs), fleet mapping, and detailed package audit trails.
- **Advanced SQL Views**: Dynamically aggregates network load across the globe using `GROUP BY` and `SUM`.
- **Interactive Terminal Interface**: A highly responsive CLI application allowing users to track packages and view analytics seamlessly.

## Getting Started

### 1. Database Setup
Ensure you have a local MySQL server running (e.g., XAMPP, WAMP, or MySQL Workbench).
1. Open your MySQL client.
2. Run the provided `schema.sql` script to create the `logistics_db` database, construct the tables, and insert dummy data.
   ```bash
   mysql -u root -p < schema.sql
   ```

### 2. Python Setup
1. Clone this repository.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Create a `.env` file in the root directory if your local MySQL requires a specific password or port:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=logistics_db
   DB_PORT=3306
   ```

### 3. Run the Application
Start the interactive terminal dashboard:
```bash
python main.py
```
