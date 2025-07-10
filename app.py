import streamlit as st
import pandas as pd
import sqlite3
import os

DB_PATH = 'plants.db'

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
    st.title("Welcome to the Therapeutic Plants Database")
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
        st.warning("No plant families found in the database. Please ensure the database is created correctly.")
        return

    # Family selection dropdown
    selected_family = st.selectbox("Select a Plant Family to browse:", families)

    if selected_family:
        try:
            # Query the database for plants in the selected family
            query = "SELECT * FROM plants WHERE Family = ?"
            df = pd.read_sql(query, conn, params=(selected_family,))
            
            st.write(f"Displaying plants from the **{selected_family}** family:")
            
            # Display the data in a more readable format
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
    st.markdown("""
    We welcome your questions, feedback, and potential collaborations. Please feel free to reach out to us.
    """)
    
    # Using a form for a cleaner layout
    with st.form("contact_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        message = st.text_area("Message")
        
        # "Submit" button
        submitted = st.form_submit_button("Submit")
        if submitted:
            # In a real application, you would handle the form submission here
            # (e.g., send an email). For this example, we'll just show a message.
            st.success("Thank you for your message! We will get back to you shortly.")

def download_page():
    """Defines the content of the Download page."""
    st.title("Download the Dataset")
    st.markdown("""
    You can download the complete dataset used in this application in CSV format.
    """)
    
    csv_file_path = 'medicinal_plants.csv'
    
    if os.path.exists(csv_file_path):
        with open(csv_file_path, "rb") as file:
            st.download_button(
                label="Download CSV",
                data=file,
                file_name="medicinal_plants_database.csv",
                mime="text/csv"
            )
    else:
        st.error(f"The file '{csv_file_path}' was not found. Please make sure it's in the correct directory.")

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Therapeutic Plants DB", layout="wide")

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Browse", "Contact", "Download"])

    # Check if the database exists. If not, prompt the user to create it.
    if not os.path.exists(DB_PATH):
        st.warning(f"Database '{DB_PATH}' not found.")
        st.info("Please run the `create_database.py` script first to set up the database.")
        st.code("python create_database.py")
        return

    # Page routing
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
