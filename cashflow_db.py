import sqlite3
import json
from datetime import datetime

# Connect to SQLite database
conn = sqlite3.connect('cashflows.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS cashflows (
        cf_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cf_date TEXT,
        pay_from_id INTEGER,
        pay_to_id INTEGER,
        cf_value REAL,
        txn_id INTEGER,
        balance REAL
    )
''')
conn.commit()

def save_cashflow(cashflow_data):
    # Save a cash flow record to the database
    cursor.execute('''
        INSERT INTO cashflows (
            cf_date, pay_from_id, pay_to_id, cf_value, txn_id, balance
        ) VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        cashflow_data['cf_date'],
        cashflow_data['pay_from_id'],
        cashflow_data['pay_to_id'],
        cashflow_data['cf_value'],
        cashflow_data['txn_id'],
        cashflow_data['balance']
    ))
    conn.commit()

def retrieve_cashflow_by_id(cf_id):
    # Retrieve a cash flow by cf_id
    cursor.execute('SELECT * FROM cashflows WHERE cf_id = ?', (cf_id,))
    return cursor.fetchone()

def search_cashflows_by_field(field, value):
    # Search cash flows by a given field
    cursor.execute(f'SELECT * FROM cashflows WHERE {field} = ?', (value,))
    return cursor.fetchall()

def update_cashflow_by_id(cf_id, new_data):
    # Update a cash flow by cf_id
    cursor.execute('''
        UPDATE cashflows SET
        cf_date = ?, pay_from_id = ?, pay_to_id = ?, cf_value = ?,
        txn_id = ?, balance = ?
        WHERE cf_id = ?
    ''', (
        new_data['cf_date'],
        new_data['pay_from_id'],
        new_data['pay_to_id'],
        new_data['cf_value'],
        new_data['txn_id'],
        new_data['balance'],
        cf_id
    ))
    conn.commit()

def delete_cashflow_by_id(cf_id):
    # Delete a cash flow by cf_id
    cursor.execute('DELETE FROM cashflows WHERE cf_id = ?', (cf_id,))
    conn.commit()

# Example usage:
cashflow_data = {
    "cf_date": "2022-01-15",
    "pay_from_id": 1,
    "pay_to_id": 2,
    "cf_value": 5000.00,
    "txn_id": 1,
    "balance": 15000.00
}

# Save a cash flow
save_cashflow(cashflow_data)

# Retrieve a cash flow by cf_id
retrieved_cashflow = retrieve_cashflow_by_id(1)
print("Retrieved Cash Flow:", retrieved_cashflow)

# Search cash flows by a field
search_result = search_cashflows_by_field("pay_from_id", 1)
print("Search Result:", search_result)

# Update a cash flow by cf_id
updated_data = {"cf_date": "2022-01-20", "cf_value": 7500.00, "pay_to_id": 3}
update_cashflow_by_id(1, cashflow_data)

# Retrieve the updated cash flow
updated_cashflow = retrieve_cashflow_by_id(1)
print("Updated Cash Flow:", updated_cashflow)

# Delete a cash flow by cf_id
delete_cashflow_by_id(1)

# Confirm deletion
deleted_cashflow = retrieve_cashflow_by_id(1)
print("Deleted Cash Flow:", deleted_cashflow)

# Close the database connection
conn.close()
