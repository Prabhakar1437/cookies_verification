import csv
import mysql.connector
from mysql.connector import Error
from datetime import datetime

def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("Connection to MySQL successful")
        
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        connection.database = db_name
        print(f"Connected to database '{db_name}'")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def create_tables(connection):
    cursor = connection.cursor()
    try:
        # Create main jobs table
        create_main_table = """
        CREATE TABLE IF NOT EXISTS company_switzerland_find_jobs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            job_title VARCHAR(255) NOT NULL,
            location VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY job_location (job_title, location)
        )
        """
        
        # Create history table with foreign key reference
        create_history_table = """
        CREATE TABLE IF NOT EXISTS company_switzerland_find_jobs_history (
            history_id INT AUTO_INCREMENT PRIMARY KEY,
            job_id INT NOT NULL,
            company_name VARCHAR(255),
            email VARCHAR(255),
            address TEXT,
            fax VARCHAR(50),
            website VARCHAR(255),
            category VARCHAR(255),
            description TEXT,
            contact_no VARCHAR(50),
            contact_1 VARCHAR(50),
            contact_2 VARCHAR(50),
            contact_3 VARCHAR(50),
            instagram VARCHAR(255),
            facebook VARCHAR(255),
            youtube VARCHAR(255),
            linkedin VARCHAR(255),
            tiktok VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES company_switzerland_find_jobs(id)
        )
        """
        
        cursor.execute(create_main_table)
        cursor.execute(create_history_table)
        connection.commit()
        print("Tables created successfully")
    except Error as e:
        print(f"Error creating tables: {e}")
    finally:
        cursor.close()

def parse_contact_numbers(contact_string):
    if not contact_string:
        return [''] * 4
    
    contacts = [num.strip() for num in contact_string.split(',')]
    contacts.extend([''] * (4 - len(contacts)))
    return contacts[:4]

def parse_social_links(social_string):
    social_links = {
        'instagram': '',
        'facebook': '',
        'youtube': '',
        'linkedin': '',
        'tiktok': ''
    }
    
    if social_string:
        links = [link.strip() for link in social_string.split(',')]
        for link in links:
            link = link.lower()
            for platform in social_links.keys():
                if platform in link:
                    social_links[platform] = link
    
    return social_links

def insert_job(connection, job_title, location):
    cursor = connection.cursor()
    try:
        # Insert into main jobs table
        insert_query = """
        INSERT INTO company_switzerland_find_jobs (job_title, location)
        VALUES (%s, %s)
        """
        cursor.execute(insert_query, (job_title, location))
        connection.commit()
        return cursor.lastrowid
    except Error as e:
        if e.errno == 1062:  # Duplicate entry error
            # Get the ID of existing job
            cursor.execute("""
                SELECT id FROM company_switzerland_find_jobs 
                WHERE job_title = %s AND location = %s
            """, (job_title, location))
            return cursor.fetchone()[0]
        else:
            print(f"Error inserting job: {e}")
            return None
    finally:
        cursor.close()

def insert_job_history(connection, job_id, data):
    cursor = connection.cursor()
    try:
        insert_query = """
        INSERT INTO company_switzerland_find_jobs_history (
            job_id, company_name, email, address, fax, website, 
            category, description, contact_no, contact_1, contact_2, 
            contact_3, instagram, facebook, youtube, linkedin, tiktok
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        values = (
            job_id,
            data['company_name'],
            data['email'],
            data['address'],
            data['fax'],
            data['website'],
            data['category'],
            data['description'],
            data['contacts'][0],
            data['contacts'][1],
            data['contacts'][2],
            data['contacts'][3],
            data['social_links']['instagram'],
            data['social_links']['facebook'],
            data['social_links']['youtube'],
            data['social_links']['linkedin'],
            data['social_links']['tiktok']
        )
        
        cursor.execute(insert_query, values)
        connection.commit()
        print(f"Inserted history record for job_id: {job_id}")
        return True
    except Error as e:
        print(f"Error inserting job history: {e}")
        return False
    finally:
        cursor.close()

def process_csv_file(connection, file_path):
    total_processed = 0
    total_skipped = 0
    
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            # Process main job data
            job_title = row['industrie'].strip()
            location = row['location'].strip()
            
            # Insert job and get job_id
            job_id = insert_job(connection, job_title, location)
            
            if job_id:
                # Process additional data for history table
                contacts = parse_contact_numbers(row.get('telephone', ''))
                social_links = parse_social_links(row.get('social_links', ''))
                
                history_data = {
                    'company_name': row.get('title', '').strip(),
                    'email': row.get('email', '').strip(),
                    'address': row.get('address', '').strip(),
                    'fax': row.get('fax', '').strip(),
                    'website': row.get('website', '').strip(),
                    'category': row.get('category', '').strip(),
                    'description': row.get('description', '').strip(),
                    'contacts': contacts,
                    'social_links': social_links
                }
                
                if insert_job_history(connection, job_id, history_data):
                    total_processed += 1
                else:
                    total_skipped += 1
            else:
                total_skipped += 1
    
    print(f"\nProcessing completed:")
    print(f"Total processed: {total_processed}")
    print(f"Total skipped: {total_skipped}")

def main():
    host = "localhost"
    user = "root"
    password = "Vats@1437"
    database = "industries_last"
    csv_file = 'data_export.csv'

    # Create connection
    connection = create_connection(host, user, password, database)
    
    if connection is not None:
        try:
            # Create tables
            create_tables(connection)
            
            # Process CSV file
            process_csv_file(connection, csv_file)
            
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            connection.close()
            print("Database connection closed.")
    else:
        print("Failed to connect to the database.")

if __name__ == "__main__":
    main()