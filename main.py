import os
import sys
import mysql.connector
from tabulate import tabulate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Establish connection to local MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "logistics_db"),
            port=os.getenv("DB_PORT", "3306")
        )
        return conn
    except mysql.connector.Error as err:
        print(f"\n[ERROR] Database connection failed: {err}")
        print("Please ensure your local MySQL server is running and the database exists.")
        sys.exit(1)

def print_table(cursor, title):
    """Fetch all rows from cursor and print them as a formatted table."""
    rows = cursor.fetchall()
    if not rows:
        print(f"\n--- {title} ---")
        print("No records found.")
        return

    # Get column names
    column_names = [i[0] for i in cursor.description]
    
    print(f"\n--- {title} ---")
    print(tabulate(rows, headers=column_names, tablefmt="grid"))

def view_analytics():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Aggregation Query
        cursor.execute("""
            SELECT COUNT(*) AS total_shipments, 
                   SUM(shipping_cost) AS total_revenue 
            FROM shipments
        """)
        print_table(cursor, "Overall Network Metrics")

        # View Query
        cursor.execute("SELECT * FROM active_hub_loads")
        print_table(cursor, "Active Hub Loads (SQL View)")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        cursor.close()
        conn.close()

def view_fleet():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Join Query
        cursor.execute("""
            SELECT f.vehicle_id, f.vehicle_type, f.status, h.name AS current_hub 
            FROM fleet f 
            LEFT JOIN hubs h ON f.current_hub_id = h.hub_id
        """)
        print_table(cursor, "Global Fleet Status")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        cursor.close()
        conn.close()

def track_shipment():
    shipment_id = input("\nEnter Shipment ID (e.g. SHP-998877): ").strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Complex Join Query for Tracking Details
        query = """
            SELECT s.shipment_id, s.status, s.weight_kg, u.name AS customer, 
                   o.name AS origin, d.name AS destination
            FROM shipments s
            JOIN users u ON s.customer_id = u.user_id
            JOIN hubs o ON s.origin_hub_id = o.hub_id
            JOIN hubs d ON s.dest_hub_id = d.hub_id
            WHERE s.shipment_id = %s
        """
        cursor.execute(query, (shipment_id,))
        rows = cursor.fetchall()
        
        if not rows:
            print("\n[ERROR] Shipment not found.")
            return

        column_names = [i[0] for i in cursor.description]
        print("\n--- Shipment Details ---")
        print(tabulate(rows, headers=column_names, tablefmt="grid"))

        # Tracking Logs
        log_query = """
            SELECT t.timestamp, t.action, COALESCE(h.name, 'In Transit') AS location
            FROM tracking_logs t
            LEFT JOIN hubs h ON t.hub_id = h.hub_id
            WHERE t.shipment_id = %s
            ORDER BY t.timestamp DESC
        """
        cursor.execute(log_query, (shipment_id,))
        print_table(cursor, "Tracking Timeline")
        
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        cursor.close()
        conn.close()

def main_menu():
    while True:
        print("\n=============================================")
        print("  🏢 Enterprise Supply Chain DBMS (Local)  ")
        print("=============================================")
        print("1. View Global Analytics")
        print("2. View Fleet Status")
        print("3. Track a Shipment")
        print("4. Exit")
        print("=============================================")
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == '1':
            view_analytics()
        elif choice == '2':
            view_fleet()
        elif choice == '3':
            track_shipment()
        elif choice == '4':
            print("\nExiting system. Goodbye!")
            sys.exit(0)
        else:
            print("\n[ERROR] Invalid option. Please try again.")

if __name__ == "__main__":
    main_menu()
