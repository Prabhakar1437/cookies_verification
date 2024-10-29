#This is final code of find_job_history of all field
import csv
import mysql.connector
from mysql.connector import Error

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

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def check_exists_in_main_table(connection, job_title, location):
    query = """
    SELECT COUNT(*) FROM company_switzerland_find_jobs
    WHERE job_title = %s AND location = %s
    """
    cursor = connection.cursor()
    cursor.execute(query, (job_title, location))
    result = cursor.fetchone()[0]
    return result > 0

def check_exists_in_history_table(connection, job_title, location, company_name):
    query = """
    SELECT COUNT(*) FROM company_switzerland_find_jobs_history
    WHERE job_title = %s AND location = %s AND company_name = %s
    """
    cursor = connection.cursor()
    cursor.execute(query, (job_title, location, company_name))
    result = cursor.fetchone()[0]
    return result > 0

def parse_contact_numbers(contact_string):
    # Split contact numbers by comma and clean them
    if not contact_string:
        return [''] * 4  # Return 4 empty strings if no contact numbers
    
    contacts = [num.strip() for num in contact_string.split(',')]
    # Pad with empty strings if less than 4 numbers provided
    contacts.extend([''] * (4 - len(contacts)))
    # Return only first 4 numbers if more are provided
    return contacts[:4]

def parse_social_links(social_string):
    # Initialize empty dictionary with all social media platforms
    social_links = {
        'instagram': '',
        'facebook': '',
        'youtube': '',
        'linkedin': '',
        'tiktok': ''
    }
    
    if social_string:
        # Split the social links by comma
        links = [link.strip() for link in social_string.split(',')]
        
        # Process each link and categorize it
        for link in links:
            link = link.lower()
            if 'instagram' in link:
                social_links['instagram'] = link
            elif 'facebook' in link:
                social_links['facebook'] = link
            elif 'youtube' in link:
                social_links['youtube'] = link
            elif 'linkedin' in link:
                social_links['linkedin'] = link
            elif 'tiktok' in link:
                social_links['tiktok'] = link
    
    return social_links

def insert_history_data(connection, data):
    if not check_exists_in_main_table(connection, data['job_title'], data['location']):
        print(f"Skipping: {data['job_title']} - {data['location']} not found in main table")
        return False
    
    if check_exists_in_history_table(connection, data['job_title'], data['location'], data['company_name']):
        print(f"Skipping existing record: {data['job_title']} - {data['location']} - {data['company_name']}")
        return False
    
    query = """
    INSERT INTO company_switzerland_find_jobs_history 
    (job_title, location, company_name, email, address, fax, website, category, description,
     contact_no, contact_1, contact_2, contact_3,
     instagram, facebook, youtube, linkedin, tiktok)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query, (
            data['job_title'],
            data['location'],
            data['company_name'],
            data['email'],
            data['address'],
            data['fax'],
            data['website'],
            data['category'],
            data['description'],
            data['contacts'][0],  # contact_no
            data['contacts'][1],  # contact_1
            data['contacts'][2],  # contact_2
            data['contacts'][3],  # contact_3
            data['social_links']['instagram'],
            data['social_links']['facebook'],
            data['social_links']['youtube'],
            data['social_links']['linkedin'],
            data['social_links']['tiktok']
        ))
        connection.commit()
        print(f"Inserted history record: {data['job_title']} - {data['location']} - {data['company_name']}")
        return True
    except Error as e:
        print(f"The error '{e}' occurred")
        return False

def main():
    host = "localhost"
    user = "root"
    password = "Vats@1437"
    database = "industries_d"

    connection = create_connection(host, user, password, database)

    if connection is not None:
        # Create history table if it does not exist
        create_history_table_query = """
        CREATE TABLE IF NOT EXISTS company_switzerland_find_jobs_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            job_title VARCHAR(255) NOT NULL,
            location VARCHAR(255) NOT NULL,
            company_name VARCHAR(255) NOT NULL,
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
            UNIQUE KEY job_location_company (job_title, location, company_name)
        )
        """
        execute_query(connection, create_history_table_query)

        # Read data from the new CSV file
        total_inserted = 0
        total_skipped = 0

        with open('data_export.csv', 'r', encoding='utf-8') as data_file:
            data_reader = csv.DictReader(data_file)

            for row in data_reader:
                # Parse contact numbers and social links
                contacts = parse_contact_numbers(row.get('telephone', ''))
                social_links = parse_social_links(row.get('social_links', ''))

                data = {
                    'job_title': row['industrie'].strip(),
                    'location': row['location'].strip(),
                    'company_name': row['title'].strip(),
                    'email': row.get('email', '').strip(),
                    'address': row.get('address', '').strip(),
                    'fax': row.get('fax', '').strip(),
                    'website': row.get('website', '').strip(),
                    'category': row.get('category', '').strip(),
                    'description': row.get('description', '').strip(),
                    'contacts': contacts,
                    'social_links': social_links
                }

                if insert_history_data(connection, data):
                    total_inserted += 1
                else:
                    total_skipped += 1

        print(f"Data insertion completed. Inserted: {total_inserted}, Skipped: {total_skipped}")
    else:
        print("Failed to connect to the database.")

if __name__ == "__main__":
    main()