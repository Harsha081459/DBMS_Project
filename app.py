import streamlit as st
import mysql.connector
import os
from dotenv import load_dotenv
import pandas as pd
import uuid

# Load local environment variables if they exist
load_dotenv()

st.set_page_config(page_title="Enterprise Supply Chain DBMS", page_icon="🏢", layout="wide")

# Database Connection
@st.cache_resource
def get_db_connection():
    try:
        db_host = st.secrets["DB_HOST"] if "DB_HOST" in st.secrets else os.getenv("DB_HOST", "localhost")
        db_user = st.secrets["DB_USER"] if "DB_USER" in st.secrets else os.getenv("DB_USER", "root")
        db_password = st.secrets["DB_PASSWORD"] if "DB_PASSWORD" in st.secrets else os.getenv("DB_PASSWORD", "")
        db_name = st.secrets["DB_NAME"] if "DB_NAME" in st.secrets else os.getenv("DB_NAME", "test")
        db_port = st.secrets["DB_PORT"] if "DB_PORT" in st.secrets else os.getenv("DB_PORT", "4000")
        
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port,
            ssl_verify_cert=False,
            ssl_verify_identity=False
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Helper to run read queries
def run_query(query, params=None):
    conn = get_db_connection()
    if conn:
        df = pd.read_sql(query, conn, params=params)
        return df
    return pd.DataFrame()

# Initialize Database Schema from schema.sql
def reset_database():
    conn = get_db_connection()
    if conn:
        with open("schema.sql", "r") as f:
            sql_script = f.read()
            
        cursor = conn.cursor()
        # Execute each statement (mysql.connector doesn't support executing entire script at once easily)
        statements = sql_script.split(';')
        for stmt in statements:
            if stmt.strip():
                try:
                    cursor.execute(stmt)
                except Exception as e:
                    pass # Ignore errors for views/drops
        conn.commit()
        cursor.close()
        st.success("Database successfully reset and seeded!")

# UI Header
st.title("🏢 Enterprise Supply Chain DBMS")
st.markdown("Advanced Database Management System demonstrating relational schema, complex joins, and SQL aggregations.")

with st.sidebar:
    st.header("Admin Controls")
    if st.button("⚠️ Factory Reset Database (Run schema.sql)"):
        reset_database()
    st.markdown("---")
    st.write("Logged in as: **System Admin**")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Analytics Dashboard", "🏢 Hubs & Fleet", "📦 Operations", "🔍 Customer Tracking"])

# --- TAB 1: Analytics Dashboard (Complex Aggregations) ---
with tab1:
    st.header("Global Network Analytics")
    st.markdown("Metrics generated using SQL `SUM`, `COUNT`, `GROUP BY`, and Views.")
    
    col1, col2, col3 = st.columns(3)
    
    # KPI 1: Total Active Shipments
    df_active = run_query("SELECT COUNT(*) as count, SUM(weight_kg) as weight FROM shipments WHERE status IN ('Manifested', 'In Transit')")
    if not df_active.empty:
        col1.metric("Active Shipments", df_active['count'].iloc[0], f"{df_active['weight'].iloc[0]} kg in transit")
        
    # KPI 2: Fleet Utilization
    df_fleet = run_query("SELECT COUNT(*) as count FROM fleet WHERE status = 'In Transit'")
    df_total_fleet = run_query("SELECT COUNT(*) as count FROM fleet")
    if not df_fleet.empty and not df_total_fleet.empty:
        col2.metric("Active Fleet", f"{df_fleet['count'].iloc[0]} / {df_total_fleet['count'].iloc[0]}", "Vehicles deployed")
        
    # KPI 3: Total Revenue
    df_rev = run_query("SELECT SUM(shipping_cost) as rev FROM shipments")
    if not df_rev.empty:
        col3.metric("Lifetime Revenue", f"${df_rev['rev'].iloc[0]:,.2f}")
        
    st.subheader("Active Hub Loads (SQL View)")
    df_hub_loads = run_query("SELECT * FROM active_hub_loads")
    st.dataframe(df_hub_loads, use_container_width=True)

# --- TAB 2: Hubs & Fleet (Relational Data) ---
with tab2:
    st.header("Infrastructure Management")
    colA, colB = st.columns(2)
    
    with colA:
        st.subheader("Warehouses (Hubs)")
        df_hubs = run_query("SELECT * FROM hubs")
        st.dataframe(df_hubs, use_container_width=True, hide_index=True)
        
    with colB:
        st.subheader("Transport Fleet")
        # SQL Join to get hub name
        fleet_query = '''
            SELECT f.vehicle_id, f.vehicle_type, f.capacity_kg, f.status, h.name as current_location
            FROM fleet f
            LEFT JOIN hubs h ON f.current_hub_id = h.hub_id
        '''
        df_fleet_list = run_query(fleet_query)
        st.dataframe(df_fleet_list, use_container_width=True, hide_index=True)

# --- TAB 3: Operations (CRUD) ---
with tab3:
    st.header("Logistics Operations")
    
    # Fetch lookups
    df_customers = run_query("SELECT user_id, name FROM users WHERE role='Customer'")
    df_hubs_lookup = run_query("SELECT hub_id, name FROM hubs")
    
    if not df_customers.empty and not df_hubs_lookup.empty:
        with st.form("new_shipment"):
            st.subheader("Create New Shipment")
            col1, col2 = st.columns(2)
            with col1:
                customer = st.selectbox("Customer", df_customers['name'].tolist())
                origin = st.selectbox("Origin Hub", df_hubs_lookup['name'].tolist())
                weight = st.number_input("Weight (kg)", min_value=1.0, value=10.0)
            with col2:
                cargo = st.selectbox("Cargo Type", ["Standard", "Electronics", "Perishable", "Hazardous"])
                dest = st.selectbox("Destination Hub", df_hubs_lookup['name'].tolist(), index=1)
                cost = st.number_input("Shipping Cost ($)", min_value=0.0, value=50.0)
            
            if st.form_submit_button("Manifest Shipment"):
                cust_id = int(df_customers[df_customers['name'] == customer]['user_id'].iloc[0])
                orig_id = int(df_hubs_lookup[df_hubs_lookup['name'] == origin]['hub_id'].iloc[0])
                dest_id = int(df_hubs_lookup[df_hubs_lookup['name'] == dest]['hub_id'].iloc[0])
                
                new_id = "SHP-" + str(uuid.uuid4().hex[:6]).upper()
                
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO shipments (shipment_id, customer_id, origin_hub_id, dest_hub_id, weight_kg, cargo_type, shipping_cost)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''', (new_id, cust_id, orig_id, dest_id, weight, cargo, cost))
                    
                    cursor.execute('''
                        INSERT INTO tracking_logs (shipment_id, hub_id, action)
                        VALUES (%s, %s, 'Manifest Created')
                    ''', (new_id, orig_id))
                    
                    conn.commit()
                    st.success(f"Shipment {new_id} manifested successfully!")

# --- TAB 4: Customer Tracking (Complex Joins) ---
with tab4:
    st.header("Customer Portal")
    search_id = st.text_input("Enter Shipment ID (e.g. SHP-998877)")
    
    if st.button("Track") and search_id:
        # Complex join query
        track_query = '''
            SELECT 
                s.shipment_id, s.status, s.cargo_type, s.weight_kg,
                u.name as customer_name,
                o.name as origin,
                d.name as destination
            FROM shipments s
            JOIN users u ON s.customer_id = u.user_id
            JOIN hubs o ON s.origin_hub_id = o.hub_id
            JOIN hubs d ON s.dest_hub_id = d.hub_id
            WHERE s.shipment_id = %s
        '''
        df_pkg = run_query(track_query, (search_id,))
        
        if not df_pkg.empty:
            st.subheader(f"Package: {df_pkg['shipment_id'].iloc[0]} ({df_pkg['status'].iloc[0]})")
            st.write(f"**Customer:** {df_pkg['customer_name'].iloc[0]} | **Route:** {df_pkg['origin'].iloc[0]} ➡️ {df_pkg['destination'].iloc[0]}")
            
            st.markdown("### Tracking Timeline")
            log_query = '''
                SELECT t.timestamp, t.action, COALESCE(h.name, 'In Transit') as location
                FROM tracking_logs t
                LEFT JOIN hubs h ON t.hub_id = h.hub_id
                WHERE t.shipment_id = %s
                ORDER BY t.timestamp DESC
            '''
            df_logs = run_query(log_query, (search_id,))
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
        else:
            st.error("Shipment not found.")
