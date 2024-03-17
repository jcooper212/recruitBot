import sqlite3
import json
from datetime import datetime

# Connect to SQLite database
conn = sqlite3.connect('transactions.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        hiring_mgr TEXT,
        client_price REAL,
        referral_commission REAL,
        referral_name TEXT,
        referral_price REAL,
        recruiter_name TEXT,
        recruiter_price REAL,
        candidate_name TEXT,
        candidate_role TEXT,
        location TEXT,
        start_date TEXT,
        end_date TEXT,
        num_payments_received INTEGER,
        total_client_recv REAL,
        total_provider_paid REAL,
        last_payment_date TEXT
    )
''')
conn.commit()

def save_transaction(transaction_data):
    # Save a transaction record to the database
    cursor.execute('''
        INSERT INTO transactions (
            client_name, hiring_mgr, client_price, referral_commission,
            referral_name, referral_price, recruiter_name, recruiter_price,
            candidate_name, candidate_role, location, start_date, end_date,
            num_payments_received, total_client_recv, total_provider_paid, last_payment_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        transaction_data['client_name'],
        transaction_data['hiring_mgr'],
        transaction_data['client_price'],
        transaction_data['referral_commission'],
        transaction_data['referral_name'],
        transaction_data['referral_price'],
        transaction_data['recruiter_name'],
        transaction_data['recruiter_price'],
        transaction_data['candidate_name'],
        transaction_data['candidate_role'],
        transaction_data['location'],
        transaction_data['start_date'],
        transaction_data['end_date'],
        transaction_data['num_payments_received'],
        transaction_data['total_client_recv'],
        transaction_data['total_provider_paid'],
        transaction_data['last_payment_date']
    ))
    conn.commit()

def retrieve_transaction_by_id(txn_id):
    # Retrieve a transaction by txn_id
    cursor.execute('SELECT * FROM transactions WHERE txn_id = ?', (txn_id,))
    return cursor.fetchone()

def search_transactions_by_field(field, value):
    # Search transactions by a given field
    cursor.execute(f'SELECT * FROM transactions WHERE {field} = ?', (value,))
    return cursor.fetchall()

def update_transaction_by_id(txn_id, new_data):
    # Update a transaction by txn_id
    cursor.execute('''
        UPDATE transactions SET
        client_name = ?, hiring_mgr = ?, client_price = ?, referral_commission = ?,
        referral_name = ?, referral_price = ?, recruiter_name = ?, recruiter_price = ?,
        candidate_name = ?, candidate_role = ?, location = ?, start_date = ?, end_date = ?,
        num_payments_received = ?, total_client_recv = ?, total_provider_paid = ?,
        last_payment_date = ?
        WHERE txn_id = ?
    ''', (
        new_data['client_name'],
        new_data['hiring_mgr'],
        new_data['client_price'],
        new_data['referral_commission'],
        new_data['referral_name'],
        new_data['referral_price'],
        new_data['recruiter_name'],
        new_data['recruiter_price'],
        new_data['candidate_name'],
        new_data['candidate_role'],
        new_data['location'],
        new_data['start_date'],
        new_data['end_date'],
        new_data['num_payments_received'],
        new_data['total_client_recv'],
        new_data['total_provider_paid'],
        new_data['last_payment_date'],
        txn_id
    ))
    conn.commit()

def delete_transaction_by_id(txn_id):
    # Delete a transaction by txn_id
    cursor.execute('DELETE FROM transactions WHERE txn_id = ?', (txn_id,))
    conn.commit()

def print_all_records():
    # Print and return all records as JSON objects
    cursor.execute('SELECT * FROM transactions')
    all_records = cursor.fetchall()

    records_json = [dict(zip([column[0] for column in cursor.description], record)) for record in all_records]

    for record in records_json:
        print(record)

    return records_json

def add_records_from_json_file(file_path):
    # Read records from a JSON file and add them to the database
    with open(file_path, 'r') as file:
        records = json.load(file)

    for record in records:
        save_transaction(record)

# Example usage:
transaction_data = {
    "client_name": "ABC Corporation",
    "hiring_mgr": "John Manager",
    "client_price": 100000.00,
    "referral_commission": 5000.00,
    "referral_name": "Referrer",
    "referral_price": 1000.00,
    "recruiter_name": "Recruiter",
    "recruiter_price": 8000.00,
    "candidate_name": "John Doe",
    "candidate_role": "Software Engineer",
    "location": "City",
    "start_date": "2022-01-01",
    "end_date": "2022-12-31",
    "num_payments_received": 12,
    "total_client_recv": 95000.00,
    "total_provider_paid": 75000.00,
    "last_payment_date": "2022-12-15"
}

# Save a transaction
save_transaction(transaction_data)

# Retrieve a transaction by txn_id
retrieved_transaction = retrieve_transaction_by_id(1)
print("Retrieved Transaction:", retrieved_transaction)

# Search transactions by a field
search_result = search_transactions_by_field("client_name", "ABC Corporation")
print("Search Result:", search_result)

# Update a transaction by txn_id
updated_data = {"client_name": "XYZ Corporation", "client_price": 120000.00, "hiring_mgr": "New Manager"}
update_transaction_by_id(1, transaction_data)

# Retrieve the updated transaction
updated_transaction = retrieve_transaction_by_id(1)
print("Updated Transaction:", updated_transaction)

# Delete a transaction by txn_id
delete_transaction_by_id(1)

# Confirm deletion
deleted_transaction = retrieve_transaction_by_id(1)
print("Deleted Transaction:", deleted_transaction)

json_records = print_all_records()

json_file_path = './transactions.json'
add_records_from_json_file(json_file_path)

# Close the database connection
conn.close()
