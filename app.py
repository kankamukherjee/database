import streamlit as st
import pandas as pd
import sqlite3
import os

DB_PATH = 'plants.db'
CSV_PATH = 'medicinal_plants.csv'

# --- DATABASE SETUP (No changes needed here) ---
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

# --- CUSTOM STYLING (Inspired by your screenshots) ---
def load_custom_css():
    """Injects custom CSS to style the app like the screenshots."""
    st.markdown("""
        <style>
            /* Main theme colors */
            .stApp {
                background-color: #e8f5e9; /* Light green background */
            }
            
            /* Main content area */
            [data-testid="stAppViewContainer"] > .main {
                background-color: #f1f8e9; /* Lighter green for content */
                border: 2px solid #a5d6a7;
                border-radius: 10px;
                padding: 2rem;
            }

            /* Sidebar styling */
            [data-testid="stSidebar"] {
                background-color: #c8e6c9; /* Slightly darker green for sidebar */
                border-right: 2px solid #a5d6a7;
            }
            [data-testid="stSidebar"] h1 {
                color: #1b5e20; /* Dark green for sidebar title */
                text-align: center;
            }
            .st-emotion-cache-1cypcdb { /* Sidebar radio buttons */
                background-color: #e8f5e9;
                border-radius: 5px;
                padding: 10px;
                border: 1px solid #a5d6a7;
            }

            /* Page titles */
            h1, h2 {
                color: #2e7d32; /* Darker green for titles */
                border-bottom: 2px solid #a5d6a7;
                padding-bottom: 5px;
            }

            /* Subheaders for plant names */
            h3 {
                color: #388e3c;
            }

            /* Custom expander styling */
            .st-emotion-cache-p5msec { /* Expander header */
                background-color: #dcedc8;
                border-radius: 5px;
            }
            
            /* Custom button styling */
            .stButton > button {
                background-color: #4caf50;
                color: white;
                border-radius: 5px;
                border: none;
                padding: 10px 20px;
            }
            .stButton > button:hover {
                background-color: #66bb6a;
            }
            
            /* Circular images for home page */
            .circular-image img {
                border: 4px solid #a5d6a7;
                border-radius: 50%;
                width: 150px;
                height: 150px;
                object-fit: cover;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .image-caption {
                text-align: center;
                color: #1b5e20;
                font-weight: bold;
                margin-top: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

# --- PAGE DEFINITIONS ---
def home_page():
    """Defines the content of the Home page with interactive elements."""
    st.title("Plant Therapeutic Database")
    st.markdown("""
    Welcome! This database is a dedicated resource for exploring the therapeutic properties of plants from the North-Eastern region of India. Browse through different plant families, search for specific information, and download the data for your own research.
    """)
    st.divider()

    st.header("Featured Plant Families")
    
    # Example of an interactive, visually appealing layout
    cols = st.columns(4)
    families_to_feature = ["Polygonaceae", "Rosaceae", "Rubiaceae", "Rutaceae"]
    placeholders = [
        "https://placehold.co/150x150/81c784/ffffff?text=Polygonum",
        "https://placehold.co/150x150/a5d6a7/ffffff?text=Rose",
        "https://placehold.co/150x150/66bb6a/ffffff?text=Coffee",
        "https://placehold.co/150x150/4caf50/ffffff?text=Citrus"
    ]

    for i, col in enumerate(cols):
        with col:
            st.markdown(f'<div class="circular-image"><img src="{placeholders[i]}" alt="{families_to_feature[i]}"></div>', unsafe_allow_html=True)
            st.markdown(f'<p class="image-caption">{families_to_feature[i]}</p>', unsafe_allow_html=True)

def browse_page():
    """Defines the content of the Browse page with expandable sections."""
    st.title("Browse by Plant Family")
    st.markdown("Select a plant family to see the species and their details.")

    conn = get_db_connection()
    if not conn: return

    try:
        # Fetch families and the plants within them
        families_df = pd.read_sql("SELECT DISTINCT Family FROM plants ORDER BY Family", conn)
        plants_df = pd.read_sql("SELECT Name_of_Plant, Scientific_Name, Family, Therapeutic_Use, Tissue_Part, Preparation_Method, Phytochemicals FROM plants", conn)

        for family in families_df['Family']:
            with st.expander(f"Family: {family}"):
                family_plants = plants_df[plants_df['Family'] == family]
                if not family_plants.empty:
                    for _, row in family_plants.iterrows():
                        st.subheader(row['Name_of_Plant'])
                        st.markdown(f"**Scientific Name:** *{row['Scientific_Name']}*")
                        st.markdown(f"**Therapeutic Use:** {row['Therapeutic_Use']}")
                        st.markdown(f"**Tissue & Part:** {row['Tissue_Part']}")
                        st.markdown(f"**Preparation Method:** {row['Preparation_Method']}")
                        st.markdown(f"**Phytochemical(s):** {row['Phytochemicals']}")
                        st.markdown("---")
                else:
                    st.write("No plants listed for this family.")
    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")
    
    conn.close()

def search_page():
    """Defines the content of the Advanced Search page."""
    st.title("Advanced Search")
    st.markdown("Use the fields below to perform a detailed search.")

    with st.form("search_form"):
        col1, col2 = st.columns(2)
        with col1:
            name_query = st.text_input("Plant Name (Common or Scientific)")
            use_query = st.text_input("Therapeutic Use")
        with col2:
            family_query = st.text_input("Plant Family")
            phytochemical_query = st.text_input("Phytochemical")
        
        submitted = st.form_submit_button("Search")

    if submitted:
        conn = get_db_connection()
        if not conn: return
        
        # Build the query dynamically
        query = "SELECT * FROM plants WHERE 1=1"
        params = []
        if name_query:
            query += " AND (Name_of_Plant LIKE ? OR Scientific_Name LIKE ?)"
            params.extend([f'%{name_query}%', f'%{name_query}%'])
        if use_query:
            query += " AND Therapeutic_Use LIKE ?"
            params.append(f'%{use_query}%')
        if family_query:
            query += " AND Family LIKE ?"
            params.append(f'%{family_query}%')
        if phytochemical_query:
            query += " AND Phytochemicals LIKE ?"
            params.append(f'%{phytochemical_query}%')
        
        try:
            results_df = pd.read_sql(query, conn, params=tuple(params))
            st.write(f"Found **{len(results_df)}** results.")
            st.dataframe(results_df)
        except Exception as e:
            st.error(f"Search error: {e}")
        
        conn.close()

def contact_page():
    """Defines the content of the Contact page."""
    st.title("Contact Us")
    st.markdown("We welcome your questions, feedback, and potential collaborations.")
    
    with st.form("contact_form"):
        col1, col2 = st.columns([1, 2])
        with col1:
             st.image("https://placehold.co/200x200/a5d6a7/1b5e20?text=Contact", use_column_width=True)
        with col2:
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            message = st.text_area("Message", height=150)
        
        submitted = st.form_submit_button("Submit Message")
        if submitted:
            st.success("Thank you! Your message has been sent.")

def download_page():
    """Defines the content of the Download page."""
    st.title("Download the Dataset")
    st.markdown("You can download the complete dataset used in this application in CSV format.")
    
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, "rb") as file:
            st.download_button(
                label="Download CSV",
                data=file,
                file_name="medicinal_plants_database.csv",
                mime="text/csv"
            )
    else:
        st.error(f"The data file '{CSV_PATH}' was not found.")

# --- MAIN APP LOGIC ---
def main():
    st.set_page_config(page_title="Plant DB", layout="wide")
    
    # Apply custom styling
    load_custom_css()
    
    # Ensure database is ready
    setup_database()

    st.sidebar.title("Main Menu")
    page_options = ["Home", "Browse", "Advanced Search", "Contact", "Download"]
    page = st.sidebar.radio("Navigate", page_options)
    
    st.sidebar.markdown("---")
    st.sidebar.info("© 2025 Plant Therapeutic DB")

    if page == "Home":
        home_page()
    elif page == "Browse":
        browse_page()
    elif page == "Advanced Search":
        search_page()
    elif page == "Contact":
        contact_page()
    elif page == "Download":
        download_page()

if __name__ == '__main__':
