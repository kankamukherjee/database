import streamlit as st
import pandas as pd
import sqlite3
import os

DB_PATH = 'plants.db'
CSV_PATH = 'medicinal_plants.csv'

def setup_database():
    """
    Checks if the database exists. If not, it creates it from the CSV file.
    This function is designed to run once when the Streamlit app starts.
    """
    if not os.path.exists(DB_PATH):
        st.toast("Database not found. Creating it from CSV...")
        try:
            if not os.path.exists(CSV_PATH):
                st.error(f"Error: The data file '{CSV_PATH}' was not found in the repository.")
                st.stop()

            df = pd.read_csv(CSV_PATH)
            
            # Rename columns for database compatibility
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

def get_unique_families(conn):
    """Fetches unique plant families from the database."""
    if conn:
        try:
            query = "SELECT DISTINCT Family FROM plants ORDER BY Family"
            families = pd.read_sql(query, conn)['Family'].tolist()
            return families
        except Exception as e:
            st.error(f"Error fetching families: {e}")
    return []

def home_page():
    """Defines the content of the Home page."""
    st.title("Welcome to the Therapeutic Plants Database 🍃")
    st.markdown("""
    This database provides comprehensive information about therapeutic plants found in the North-Eastern region of India. 
    Our goal is to create a valuable resource for researchers, students, and enthusiasts interested in medicinal botany.

    ### Features
    - **Browse:** Explore the plant database, filtered by family.
    - **Contact:** Get in touch with us for inquiries or collaborations.
    - **Download:** Access the complete dataset in CSV format.

    Use the navigation menu on the left to explore the different sections of the application.
    """)

def browse_page():
    """Defines the content of the Browse page."""
    st.title("Browse the Plant Database")
    
    conn = get_db_connection()
    if not conn:
        return

    families = get_unique_families(conn)
    
    if not families:
        st.warning("No plant families found. The database might be empty.")
        return

    selected_family = st.selectbox("Select a Plant Family to browse:", families)

    if selected_family:
        try:
            query = "SELECT * FROM plants WHERE Family = ?"
            df = pd.read_sql(query, conn, params=(selected_family,))
            
            st.write(f"Displaying plants from the **{selected_family}** family:")
            
            if not df.empty:
                for index, row in df.iterrows():
                    st.subheader(row['Name_of_Plant'])
                    st.markdown(f"**Scientific Name:** *{row['Scientific_Name']}*")
                    st.markdown(f"**Therapeutic Use:** {row['Therapeutic_Use']}")
                    st.markdown(f"**Tissue & Part:** {row['Tissue_Part']}")
                    st.markdown(f"**Preparation Method:** {row['Preparation_Method']}")
                    st.markdown(f"**Phytochemical(s):** {row['Phytochemicals']}")
                    with st.expander("More Details"):
                        st.markdown(f"**NE State Availability:** {row['NE_State_Availability']}")
                        st.markdown(f"**Related Database:** {row['Related_Database']}")
                        st.markdown(f"**Phytochemical Reference:** {row['Phytochemical_Reference']}")
                        st.markdown(f"**Literature Reference:** {row['Literature_Reference']}")
                    st.divider()
            else:
                st.write("No plants found for this family.")

        except Exception as e:
            st.error(f"An error occurred while fetching data: {e}")
    
    conn.close()

def contact_page():
    """Defines the content of the Contact page."""
    st.title("Contact Us")
    st.markdown("We welcome your questions, feedback, and potential collaborations.")
    
    with st.form("contact_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        message = st.text_area("Message")
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.success("Thank you for your message! We will get back to you shortly.")

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
        st.error(f"The file '{CSV_PATH}' was not found.")

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Therapeutic Plants DB", layout="wide")
    
    # This is the key change: Run the setup function at the start.
    setup_database()

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Browse", "Contact", "Download"])

    if page == "Home":
        home_page()
    elif page == "Browse":
        browse_page()
    elif page == "Contact":
        contact_page()
    elif page == "Download":
        download_page()

if __name__ == '__main__':
    main()
