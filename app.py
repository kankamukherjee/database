import streamlit as st
import pandas as pd
import sqlite3
import os
import sys

# Add the root directory to the Python path to import create_database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the database setup function from create_database.py
from create_database import setup_database

DB_PATH = 'plants.db'
CSV_PATH = 'medicinal_plants.csv'

# --- DATABASE CONNECTION ---
def get_db_connection():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return None

# --- CUSTOM STYLING AND LAYOUT ---
def load_custom_css():
    """Injects custom CSS for styling."""
    st.markdown("""
        <style>
            body { background-color: #003300; }
            .stApp {
                background-color: #e8f5e9;
                border: 3px solid #006400;
                border-radius: 15px;
                padding: 1rem;
                margin: 1rem;
            }
            .custom-header {
                background-color: #006400;
                padding: 1rem;
                border-radius: 10px 10px 0 0;
                color: white;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .custom-header h1 { margin: 0; font-size: 2rem; color: #ffffff; }
            .nav-links { display: flex; gap: 15px; }
            .nav-links button {
                background-color: transparent;
                color: white;
                border: 1px solid white;
                border-radius: 5px;
                padding: 8px 15px;
                cursor: pointer;
                transition: background-color 0.3s, color 0.3s;
            }
            .nav-links button:hover, .nav-links button.active {
                background-color: #ffffff;
                color: #006400;
            }
            .custom-footer {
                text-align: center;
                padding: 1rem;
                margin-top: 2rem;
                color: #006400;
                border-top: 2px solid #a5d6a7;
            }
            .family-box {
                display: inline-block;
                width: 200px;
                height: 200px;
                background-color: #a5d6a7;
                border-radius: 50%;
                text-align: center;
                line-height: 200px;
                margin: 10px;
                color: #006400;
                font-weight: bold;
                cursor: pointer;
                transition: transform 0.3s;
            }
            .family-box:hover { transform: scale(1.1); }
            h1, h2 { color: #2e7d32; border-bottom: 2px solid #a5d6a7; padding-bottom: 5px; }
            h3 { color: #388e3c; }
        </style>
    """, unsafe_allow_html=True)

def custom_header():
    """Creates a custom header with navigation."""
    if 'page' not in st.session_state:
        st.session_state.page = 'Home'
    
    def set_page(page_name):
        st.session_state.page = page_name
    
    st.markdown('<div class="custom-header"><h1>🌿 Medicinal Plants of India DB</h1><div id="nav-container"></div></div>', unsafe_allow_html=True)
    nav_cols = st.columns(6)
    pages = ["Home", "Browse", "Search", "Statistics", "Contact", "Download"]
    for i, page in enumerate(pages):
        active_class = "active" if st.session_state.page == page else ""
        nav_cols[i].button(page, on_click=set_page, args=(page,), type="secondary", use_container_width=True)

# --- PAGE DEFINITIONS ---
def home_page():
    st.title("Welcome to Medicinal Plants of India Database")
    st.markdown("Explore the rich heritage of medicinal plants across India, organized by family and region.")
    conn = get_db_connection()
    if conn:
        try:
            families = pd.read_sql("SELECT DISTINCT Family FROM plants ORDER BY Family", conn)
            cols = st.columns(4)
            for idx, family in families.iterrows():
                with cols[idx % 4]:
                    st.markdown(f'<div class="family-box" onClick="window.location.href=\'#\'">{family["Family"]}</div>', unsafe_allow_html=True)
        finally:
            conn.close()

def browse_page():
    st.title("Browse Medicinal Plants")
    conn = get_db_connection()
    if conn:
        try:
            families_df = pd.read_sql("SELECT DISTINCT Family FROM plants ORDER BY Family", conn)
            for family in families_df['Family']:
                with st.expander(f"Family: {family}"):
                    plants_df = pd.read_sql("SELECT * FROM plants WHERE Family = ?", conn, params=(family,))
                    for _, row in plants_df.iterrows():
                        st.subheader(row['Name_of_Plant'])
                        st.markdown(f"**Scientific Name:** *{row['Scientific_Name']}*")
                        st.markdown(f"**Region:** {row['Region']}")
                        st.markdown(f"**Therapeutic Use:** {row['Therapeutic_Use']}")
                        st.markdown("---")
        finally:
            conn.close()

def search_page():
    st.title("Advanced Search")
    with st.form("search_form"):
        name = st.text_input("Plant Name (Common or Scientific)")
        region = st.selectbox("Region", ["All"] + pd.read_sql("SELECT DISTINCT Region FROM plants", get_db_connection())['Region'].tolist())
        use = st.text_input("Therapeutic Use")
        submitted = st.form_submit_button("Search")
    if submitted:
        conn = get_db_connection()
        if conn:
            try:
                query = "SELECT Name_of_Plant, Scientific_Name, Family, Region, Therapeutic_Use FROM plants WHERE (Name_of_Plant LIKE ? OR Scientific_Name LIKE ?) AND Therapeutic_Use LIKE ?"
                params = (f'%{name}%', f'%{name}%', f'%{use}%')
                if region != "All":
                    query += " AND Region = ?"
                    params += (region,)
                results_df = pd.read_sql(query, conn, params=params)
                st.write(f"Found **{len(results_df)}** results.")
                st.dataframe(results_df)
            finally:
                conn.close()

def statistics_page():
    st.title("Database Statistics")
    conn = get_db_connection()
    if conn:
        try:
            total_plants = pd.read_sql("SELECT COUNT(*) as count FROM plants", conn)['count'][0]
            total_families = pd.read_sql("SELECT COUNT(DISTINCT Family) as count FROM plants", conn)['count'][0]
            plants_per_family = pd.read_sql("SELECT Family, COUNT(*) as PlantCount FROM plants GROUP BY Family ORDER BY PlantCount DESC", conn)

            col1, col2 = st.columns(2)
            col1.metric("Total Plant Entries", total_plants)
            col2.metric("Total Plant Families", total_families)
            st.subheader("Plants per Family")
            st.bar_chart(plants_per_family.set_index('Family'))
        finally:
            conn.close()

def contact_page():
    st.title("Contact Us")
    with st.form("contact_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        message = st.text_area("Message")
        st.form_submit_button("Submit")

def download_page():
    st.title("Download the Dataset")
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, "rb") as file:
            st.download_button("Download CSV", file, "medicinal_plants_india.csv", "text/csv")

def custom_footer():
    st.markdown('<div class="custom-footer">© 2025 Medicinal Plants of India DB | Design by Shailesh Lab</div>', unsafe_allow_html=True)

# --- MAIN APP LOGIC ---
def main():
    st.set_page_config(page_title="Medicinal Plants DB", layout="wide")
    load_custom_css()
    custom_header()

    # Ensure database is set up on first run
    if not os.path.exists(DB_PATH):
        setup_database()

    page = st.session_state.get('page', 'Home')
    if page == "Home":
        home_page()
    elif page == "Browse":
        browse_page()
    elif page == "Search":
        search_page()
    elif page == "Statistics":
        statistics_page()
    elif page == "Contact":
        contact_page()
    elif page == "Download":
        download_page()
    
    custom_footer()

if __name__ == '__main__':
    main()
