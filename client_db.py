import sqlite3
import json

# Connect to SQLite database
conn = sqlite3.connect('clients.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        client_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        client_mgr TEXT,
        payment_freq TEXT,
        client_type TEXT
    )
''')
conn.commit()

def save_client(client_data):
    # Save a client record to the database
    cursor.execute('''
        INSERT INTO clients (
            client_name, client_mgr, payment_freq, client_type
        ) VALUES (?, ?, ?, ?)
    ''', (
        client_data['client_name'],
        client_data['client_mgr'],
        client_data['payment_freq'],
        client_data['client_type']
    ))
    conn.commit()

def retrieve_client_by_id(client_id):
    # Retrieve a client by client_id
    cursor.execute('SELECT * FROM clients WHERE client_id = ?', (client_id,))
    return cursor.fetchone()

def search_clients_by_field(field, value):
    # Search clients by a given field
    cursor.execute(f'SELECT * FROM clients WHERE {field} = ?', (value,))
    return cursor.fetchall()

def update_client_by_id(client_id, new_data):
    # Update a client by client_id
    cursor.execute('''
        UPDATE clients SET
        client_name = ?, client_mgr = ?, payment_freq = ?, client_type = ?
        WHERE client_id = ?
    ''', (
        new_data['client_name'],
        new_data['client_mgr'],
        new_data['payment_freq'],
        new_data['client_type'],
        client_id
    ))
    conn.commit()

def delete_client_by_id(client_id):
    # Delete a client by client_id
    cursor.execute('DELETE FROM clients WHERE client_id = ?', (client_id,))
    conn.commit()

# Example usage:
client_data = {
    "client_name": "ABC Corporation",
    "client_mgr": "John Manager",
    "payment_freq": "Monthly",
    "client_type": "Enterprise"
}

# Save a client
save_client(client_data)

# Retrieve a client by client_id
retrieved_client = retrieve_client_by_id(1)
print("Retrieved Client:", retrieved_client)

# Search clients by a field
search_result = search_clients_by_field("client_type", "Enterprise")
print("Search Result:", search_result)

# Update a client by client_id
updated_data = {"client_name": "XYZ Corporation", "client_type": "Small Business"}
update_client_by_id(1, client_data)

# Retrieve the updated client
updated_client = retrieve_client_by_id(1)
print("Updated Client:", updated_client)

# Delete a client by client_id
delete_client_by_id(1)

# Confirm deletion
deleted_client = retrieve_client_by_id(1)
print("Deleted Client:", deleted_client)

# Close the database connection
conn.close()
