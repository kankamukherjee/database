import pandas as pd
import sqlite3
import os

def create_database(csv_path='medicinal_plants.csv', db_path='plants.db'):
    """
    Reads data from a CSV file and creates an SQLite database.

    Args:
        csv_path (str): The path to the input CSV file.
        db_path (str): The path where the SQLite database will be created.
    """
    if not os.path.exists(csv_path):
        print(f"Error: The file '{csv_path}' was not found.")
        print("Please make sure your CSV file is in the same directory and named correctly.")
        return

    # Read the data from the CSV file
    try:
        df = pd.read_csv(csv_path)
        print("CSV file read successfully.")
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return

    # Rename columns to be more database-friendly (no spaces or special characters)
    df.columns = [
        'Name_of_Plant', 'Scientific_Name', 'Family', 'Related_Database',
        'Therapeutic_Use', 'Tissue_Part', 'Preparation_Method',
        'NE_State_Availability', 'Phytochemicals', 'Phytochemical_Reference',
        'Literature_Reference'
    ]

    # Create a connection to the SQLite database
    try:
        conn = sqlite3.connect(db_path)
        print(f"Database '{db_path}' created successfully.")
        
        # Write the data to a table named 'plants'
        df.to_sql('plants', conn, if_exists='replace', index=False)
        print("Data imported into 'plants' table successfully.")
        
        conn.close()
        print("Database connection closed.")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # This block will be executed when the script is run directly
    create_database()
