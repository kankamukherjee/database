import streamlit as st
import pandas as pd
import sqlite3
import os

DB_PATH = 'plants.db'
CSV_PATH = 'medicinal_plants.csv'

# --- DATABASE SETUP ---
def setup_database():
    """
    Checks if the database exists. If not, it creates it from the CSV file.
    """
    if not os.path.exists(DB_PATH):
        st.toast("Database not found. Creating it from CSV...")
        try:
            if not os.path.exists(CSV_PATH):
                st.error(f"Error: The data file '{CSV_PATH}' was not found in the repository.")
                st.stop()

            df = pd.read_csv(CSV_PATH)
            df.columns = [
                'Name_of_Plant', 'Scientific_Name', 'Family', 'Related_Database',
                'Therapeutic_Use', 'Tissue_Part', 'Preparation_Method',
                'NE_State_Availability', 'Phytochemicals', 'Phytochemical_Reference',
                'Literature_Reference'
            ]
            
            conn = sqlite3.connect(DB_PATH)
            df.to_sql('plants', conn, if_exists='replace', index=False)
            conn.close()
            st.toast("Database created successfully! ✔️")

        except Exception as e:
            st.error(f"An error occurred during database setup: {e}")
            st.stop()

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection error: {e}")
        return None

# --- CUSTOM STYLING AND LAYOUT ---
def load_custom_css():
    """Injects custom CSS to style the app."""
    st.markdown("""
        <style>
            /* Remove Streamlit's default header and footer */
            .st-emotion-cache-18ni7ap, .st-emotion-cache-h4yrc2 {
                display: none;
            }
            /* Main theme colors */
            body {
                background-color: #003300; /* Dark green background for the whole page */
            }
            .stApp {
                background-color: #e8f5e9;
                border: 3px solid #006400;
                border-radius: 15px;
                padding: 1rem;
                margin: 1rem;
            }
            
            /* Custom Header */
            .custom-header {
                background-color: #006400; /* Dark green header */
                padding: 1rem;
                border-radius: 10px 10px 0 0;
                color: white;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .custom-header h1 {
                margin: 0;
                font-size: 2rem;
                color: #ffffff;
            }
            .nav-links {
                display: flex;
                gap: 15px;
            }
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
            
            /* Custom Footer */
            .custom-footer {
                text-align: center;
                padding: 1rem;
                margin-top: 2rem;
                color: #006400;
                border-top: 2px solid #a5d6a7;
            }

            /* Page titles */
            h1, h2 {
                color: #2e7d32;
                border-bottom: 2px solid #a5d6a7;
                padding-bottom: 5px;
            }
            h3 { color: #388e3c; }
        </style>
    """, unsafe_allow_html=True)

def custom_header():
    """Creates a custom header with navigation."""
    # Initialize session state for navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'Home'

    # Function to update page state
    def set_page(page_name):
        st.session_state.page = page_name

    # Display header
    st.markdown('<div class="custom-header"><h1>🌿 Plant Therapeutic DB</h1><div id="nav-container"></div></div>', unsafe_allow_html=True)
    
    # Navigation buttons
    nav_cols = st.columns(6)
    pages = ["Home", "Browse", "Search", "Statistics", "Contact", "Download"]
    for i, page in enumerate(pages):
        active_class = "active" if st.session_state.page == page else ""
        nav_cols[i].button(page, on_click=set_page, args=(page,), type="secondary", use_container_width=True)


# --- PAGE DEFINITIONS ---
def home_page():
    st.title("Welcome to the Plant Database")
    st.markdown("This database is a dedicated resource for exploring the therapeutic properties of plants from the North-Eastern region of India.")
    st.image("https://placehold.co/1200x400/a5d6a7/1b5e20?text=Medicinal+Plants+of+NE+India", use_column_width=True)

def browse_page():
    st.title("Browse by Plant Family")
    conn = get_db_connection()
    if not conn: return
    try:
        families_df = pd.read_sql("SELECT DISTINCT Family FROM plants ORDER BY Family", conn)
        plants_df = pd.read_sql("SELECT * FROM plants", conn)
        for family in families_df['Family']:
            with st.expander(f"Family: {family}"):
                family_plants = plants_df[plants_df['Family'] == family]
                for _, row in family_plants.iterrows():
                    st.subheader(row['Name_of_Plant'])
                    st.markdown(f"**Scientific Name:** *{row['Scientific_Name']}*")
                    st.markdown(f"**Therapeutic Use:** {row['Therapeutic_Use']}")
                    st.markdown("---")
    finally:
        conn.close()

def search_page():
    st.title("Advanced Search")
    with st.form("search_form"):
        name_query = st.text_input("Plant Name (Common or Scientific)")
        use_query = st.text_input("Therapeutic Use")
        submitted = st.form_submit_button("Search")
    if submitted:
        conn = get_db_connection()
        if not conn: return
        try:
            query = "SELECT Name_of_Plant, Scientific_Name, Family, Therapeutic_Use FROM plants WHERE (Name_of_Plant LIKE ? OR Scientific_Name LIKE ?) AND Therapeutic_Use LIKE ?"
            params = (f'%{name_query}%', f'%{name_query}%', f'%{use_query}%')
            results_df = pd.read_sql(query, conn, params=params)
            st.write(f"Found **{len(results_df)}** results.")
            st.dataframe(results_df)
        finally:
            conn.close()

def statistics_page():
    st.title("Database Statistics")
    conn = get_db_connection()
    if not conn: return
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
            st.download_button("Download CSV", file, "medicinal_plants_database.csv", "text/csv")

def custom_footer():
    st.markdown('<div class="custom-footer">© 2025 Plant Therapeutic DB | Design by Shailesh Lab</div>', unsafe_allow_html=True)


# --- MAIN APP LOGIC ---
def main():
    st.set_page_config(page_title="Plant DB", layout="wide")
    
    # Load custom CSS and header
    load_custom_css()
    custom_header() # This replaces the sidebar navigation

    # Page routing based on session state
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
    
    # Load custom footer
    custom_footer()

if __name__ == '__main__':
    # Ensure database is created on first run
    setup_database()
    main()
