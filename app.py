import streamlit as st
import mysql.connector
import os
from dotenv import load_dotenv
import pandas as pd
import uuid
from datetime import datetime

# Load local environment variables if they exist
load_dotenv()

st.set_page_config(page_title="Global Logistics Tracking", page_icon="📦", layout="wide")

# Database Connection
def get_db_connection():
    try:
        # Try to use Streamlit Secrets for cloud deployment, fallback to .env for local
        db_host = st.secrets["DB_HOST"] if "DB_HOST" in st.secrets else os.getenv("DB_HOST", "localhost")
        db_user = st.secrets["DB_USER"] if "DB_USER" in st.secrets else os.getenv("DB_USER", "root")
        db_password = st.secrets["DB_PASSWORD"] if "DB_PASSWORD" in st.secrets else os.getenv("DB_PASSWORD", "")
        db_name = st.secrets["DB_NAME"] if "DB_NAME" in st.secrets else os.getenv("DB_NAME", "logistics_db")
        db_port = st.secrets["DB_PORT"] if "DB_PORT" in st.secrets else os.getenv("DB_PORT", "3306")
        
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

# Initialize Database Schema
def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
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
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracking_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tracking_number VARCHAR(50),
                status VARCHAR(50),
                location VARCHAR(100),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tracking_number) REFERENCES packages(tracking_number)
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

# Calculate shipping cost logic
def calculate_cost(weight, cargo_type):
    base_rate = 5.0 # $5 per kg
    cost = weight * base_rate
    if cargo_type == "Hazardous":
        cost *= 1.5
    elif cargo_type == "Perishable":
        cost *= 1.2
    return round(cost, 2)

# Streamlit App UI
st.title("📦 Global Logistics & Cargo Tracking Platform")
st.markdown("A simple, cloud-connected database application for logistics tracking.")

# Try to initialize DB schema on startup
init_db()

tab1, tab2, tab3 = st.tabs(["Ship a Package", "Track a Package", "Update Status (Admin)"])

# --- TAB 1: Ship a Package ---
with tab1:
    st.header("Book a New Shipment")
    with st.form("new_shipment_form"):
        col1, col2 = st.columns(2)
        with col1:
            sender = st.text_input("Sender Name")
            weight = st.number_input("Weight (kg)", min_value=0.1, value=1.0)
        with col2:
            receiver = st.text_input("Receiver Name")
            cargo_type = st.selectbox("Cargo Type", ["Standard", "Perishable", "Hazardous", "Electronics"])
        
        origin = st.text_input("Origin City / Hub")
        submit_btn = st.form_submit_button("Book Shipment")
        
        if submit_btn:
            if not sender or not receiver or not origin:
                st.warning("Please fill out all required fields.")
            else:
                tracking_num = "TRK-" + str(uuid.uuid4().hex[:8]).upper()
                cost = calculate_cost(weight, cargo_type)
                
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    # Insert into packages table
                    cursor.execute(
                        "INSERT INTO packages (tracking_number, sender_name, receiver_name, weight, cargo_type, shipping_cost, status, current_location) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (tracking_num, sender, receiver, weight, cargo_type, cost, "Manifested", origin)
                    )
                    # Insert into history table
                    cursor.execute(
                        "INSERT INTO tracking_history (tracking_number, status, location) VALUES (%s, %s, %s)",
                        (tracking_num, "Manifested", origin)
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    st.success(f"Shipment booked successfully! Your tracking number is **{tracking_num}**")
                    st.info(f"Estimated Shipping Cost: **${cost}**")

# --- TAB 2: Track a Package ---
with tab2:
    st.header("Track Your Shipment")
    search_trk = st.text_input("Enter Tracking Number (e.g., TRK-1A2B3C4D)")
    if st.button("Track Package"):
        if search_trk:
            conn = get_db_connection()
            if conn:
                # Get package details
                pkg_query = "SELECT * FROM packages WHERE tracking_number = %s"
                df_pkg = pd.read_sql(pkg_query, conn, params=(search_trk,))
                
                if not df_pkg.empty:
                    st.subheader(f"Status: {df_pkg['status'].iloc[0]} 📍 {df_pkg['current_location'].iloc[0]}")
                    st.write(f"**Sender:** {df_pkg['sender_name'].iloc[0]} | **Receiver:** {df_pkg['receiver_name'].iloc[0]}")
                    st.write(f"**Cargo:** {df_pkg['cargo_type'].iloc[0]} | **Weight:** {df_pkg['weight'].iloc[0]}kg | **Cost:** ${df_pkg['shipping_cost'].iloc[0]}")
                    
                    # Get tracking history
                    st.markdown("### Tracking Timeline")
                    hist_query = "SELECT timestamp, status, location FROM tracking_history WHERE tracking_number = %s ORDER BY timestamp DESC"
                    df_hist = pd.read_sql(hist_query, conn, params=(search_trk,))
                    st.dataframe(df_hist, use_container_width=True, hide_index=True)
                else:
                    st.error("Tracking number not found in database.")
                conn.close()

# --- TAB 3: Update Status ---
with tab3:
    st.header("Hub Worker / Admin Panel")
    st.markdown("Update the current location and status of a package in transit.")
    with st.form("update_status_form"):
        update_trk = st.text_input("Tracking Number")
        new_status = st.selectbox("New Status", ["In Transit", "Out for Delivery", "Delivered", "Delayed"])
        new_location = st.text_input("New Location (Hub/City)")
        
        update_btn = st.form_submit_button("Update System")
        
        if update_btn:
            if not update_trk or not new_location:
                st.warning("Please provide both Tracking Number and Location.")
            else:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    # Check if exists
                    cursor.execute("SELECT tracking_number FROM packages WHERE tracking_number = %s", (update_trk,))
                    if cursor.fetchone():
                        # Update master package record
                        cursor.execute(
                            "UPDATE packages SET status = %s, current_location = %s WHERE tracking_number = %s",
                            (new_status, new_location, update_trk)
                        )
                        # Add to history
                        cursor.execute(
                            "INSERT INTO tracking_history (tracking_number, status, location) VALUES (%s, %s, %s)",
                            (update_trk, new_status, new_location)
                        )
                        conn.commit()
                        st.success(f"Successfully updated {update_trk} to '{new_status}' at '{new_location}'.")
                    else:
                        st.error("Tracking number not found.")
                    
                    cursor.close()
                    conn.close()
