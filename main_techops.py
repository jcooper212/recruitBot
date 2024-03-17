from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
import openai
import os
import json
import requests

#Initialize
load_dotenv()
openai.api_key = os.getenv("OPEN_AI_KEY")
openai.organization = os.getenv("OPEN_AI_ORG")
elevenlabs_key = os.getenv("ELEVENLABS_KEY")


app = FastAPI()
conn = sqlite3.connect('hired.db')
cursor = conn.cursor()


# Define Pydantic models for request and response data
class Candidate(BaseModel):
    name: str
    role: str
    location: str
    candidate_cost: float
    phone: str
    email: str
    feedback: str
    cv_link: str
    status: str

class Client(BaseModel):
    name: str
    client_mgr: str
    payment_freq: str
    client_type: str

class Transaction(BaseModel):
    client_id: int
    client_price: float
    intro_fee: float
    intro_id: int
    recruiter_price: float
    recruiter_id: int
    candidate_id: int
    start_date: str
    end_date: str
    num_payments_received: int
    total_client_invoiced: float
    total_client_paid: float
    total_recruiter_paid: float
    total_intro_paid: float
    last_payment_date: str

class Cashflow(BaseModel):
    cf_date: str
    pay_from_id: int
    pay_to_id: int
    cf_value: float
    txn_id: int
    balance: float

# Connect to SQLite database
def connectDB():
    conn = sqlite3.connect('hired.db')
    return conn.cursor(), conn

# Function to save data to the database
def save_data(table_name, data):
    cursor, conn = connectDB()
    columns = ', '.join(data.keys())
    values = ', '.join(['?' for _ in range(len(data))])
    query = f'INSERT INTO {table_name} ({columns}) VALUES ({values})'
    cursor.execute(query, tuple(data.values()))
    conn.commit()

# Function to get all records from a table
def get_all_records(table_name):
    cursor, conn = connectDB()
    cursor.execute(f'SELECT * FROM {table_name}')
    return cursor.fetchall()

# Function to update data in the database
def update_data(table_name, record_id, data):
    cursor, conn = connectDB()
    update_values = ', '.join([f'{key} = ?' for key in data.keys()])
    query = f'UPDATE {table_name} SET {update_values} WHERE id = ?'
    cursor.execute(query, tuple(data.values()) + (record_id,))
    conn.commit()

# Function to find a record by ID
def find_record_by_id(table_name, record_id):
    cursor, conn = connectDB()
    cursor.execute(f'SELECT * FROM {table_name} WHERE id = ?', (record_id,))
    return cursor.fetchone()

# Function to find a record by name
def find_record_by_name(table_name, name):
    cursor, conn = connectDB()
    cursor.execute(f'SELECT * FROM {table_name} WHERE name = ?', (name,))
    return cursor.fetchone()

# Function to handle new candidate creation
@app.post("/new_candidate")
def create_candidate(candidate: Candidate):
    save_data('candidates', candidate.dict())
    return {"message": "Candidate created successfully"}

# Function to handle new client creation
@app.post("/new_client")
def create_client(client: Client):
    save_data('clients', client.dict())
    return {"message": "Client created successfully"}

# Function to handle new transaction creation
@app.post("/new_transaction")
def create_transaction(transaction: Transaction):
    save_data('transactions', transaction.dict())
    return {"message": "Transaction created successfully"}

# Function to handle new cashflow creation
@app.post("/new_cashflow")
def create_cashflow(cashflow: Cashflow):
    save_data('cashflows', cashflow.dict())
    return {"message": "Cashflow created successfully"}

# Function to list all candidates
@app.get("/list_candidates")
def list_candidates():
    return get_all_records('candidates')

# Function to list all clients
@app.get("/list_clients")
def list_clients():
    return get_all_records('clients')

# Function to list all transactions
@app.get("/list_transactions")
def list_transactions():
    return get_all_records('transactions')

# Function to list all cashflows
@app.get("/list_cashflows")
def list_cashflows():
    return get_all_records('cashflows')

# Function to update a candidate
@app.put("/update_candidate/{candidate_id}")
def update_candidate(candidate_id: int, candidate: Candidate):
    update_data('candidates', candidate_id, candidate.dict())
    return {"message": "Candidate updated successfully"}

# Function to update a client
@app.put("/update_client/{client_id}")
def update_client(client_id: int, client: Client):
    update_data('clients', client_id, client.dict())
    return {"message": "Client updated successfully"}

# Function to update a transaction
@app.put("/update_transaction/{transaction_id}")
def update_transaction(transaction_id: int, transaction: Transaction):
    update_data('transactions', transaction_id, transaction.dict())
    return {"message": "Transaction updated successfully"}

# Function to update a cashflow
@app.put("/update_cashflow/{cashflow_id}")
def update_cashflow(cashflow_id: int, cashflow: Cashflow):
    update_data('cashflows', cashflow_id, cashflow.dict())
    return {"message": "Cashflow updated successfully"}

# Function to find a candidate by ID
@app.get("/find_candidate/{candidate_id}")
def find_candidate(candidate_id: int):
    candidate = find_record_by_id('candidates', candidate_id)
    if candidate:
        return candidate
    else:
        raise HTTPException(status_code=404, detail="Candidate not found")

# Function to find a client by ID
@app.get("/find_client/{client_id}")
def find_client(client_id: int):
    client = find_record_by_id('clients', client_id)
    if client:
        return client
    else:
        raise HTTPException(status_code=404, detail="Client not found")

# Function to find a transaction by ID
@app.get("/find_transaction/{transaction_id}")
def find_transaction(transaction_id: int):
    transaction = find_record_by_id('transactions', transaction_id)
    if transaction:
        return transaction
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")

# Function to find a cashflow by ID
@app.get("/find_cashflow/{cashflow_id}")
def find_cashflow(cashflow_id: int):
    cashflow = find_record_by_id('cashflows', cashflow_id)
    if cashflow:
        return cashflow
    else:
        raise HTTPException(status_code=404, detail="Cashflow not found")

# Function to find a candidate by name
@app.get("/find_candidate_by_name/{name}")
def find_candidate_by_name(name: str):
    candidate = find_record_by_name('candidates', name)
    if candidate:
        return candidate
    else:
        raise HTTPException(status_code=404, detail="Candidate not found")

# Function to find a client by name
@app.get("/find_client_by_name/{client_name}")
def find_client_by_name(client_name: str):
    client = find_record_by_name('clients', client_name)
    if client:
        return client
    else:
        raise HTTPException(status_code=404, detail="Client not found")

# Function to find a transaction by name
@app.get("/find_transaction_by_name/{transaction_name}")
def find_transaction_by_name(transaction_name: str):
    # Assuming there is a name field in the transaction schema
    transaction = find_record_by_name('transactions', transaction_name)
    if transaction:
        return transaction
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")

#Function to create new DB
@app.get("/create_db")
def createDB():
    conn = sqlite3.connect('hired.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            role TEXT,
            location TEXT,
            candidate_cost REAL,
            phone TEXT,
            email TEXT,
            feedback TEXT,
            cv_link TEXT,
            status TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cashflows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cf_date TEXT,
            pay_from_id INTEGER,
            pay_to_id INTEGER,
            cf_value REAL,
            txn_id INTEGER,
            balance REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            client_mgr TEXT,
            payment_freq TEXT,
            client_type TEXT
        )
    ''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
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



# Function to preloadDB
@app.get("/preload_db")
def preloadDB():
    candidate_data = {
        "name": "John Doe",
        "role": "Software Engineer",
        "location": "City",
        "candidate_cost": 75000.00,
        "phone": "123-456-7890",
        "email": "john.doe@example.com",
        "feedback": "Positive",
        "cv_link": "https://example.com/johndoe_cv.pdf",
        "status": "Active"
    }
    save_data('candidates', candidate_data)

    cashflow_data = {
        "cf_date": "2022-01-15",
        "pay_from_id": 1,
        "pay_to_id": 2,
        "cf_value": 5000.00,
        "txn_id": 1,
        "balance": 15000.00
    }
    save_data('cashflows', cashflow_data)

    client_data = {
        "name": "ABC Corporation",
        "client_mgr": "John Manager",
        "payment_freq": "Monthly",
        "client_type": "Enterprise"
    }
    save_data('clients', client_data)

    transaction_data = {
        "name": "ABC Corporation",
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
    save_data('transactions', transaction_data)


##MAIN
if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI server using uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
