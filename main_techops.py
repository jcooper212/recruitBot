from fastapi import FastAPI, HTTPException
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
import hashlib
from pydantic import BaseModel
import sqlite3
from datetime import datetime, timedelta

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

# JWT Define a secret key (change this to a secure random value in production)
sec_value = os.getenv("RAYZE_KEY")
SECRET_KEY = str(sec_value)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

class Users(BaseModel):
    name: str
    email: str
    msg_id: str
    role: str
    password: str

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

class Invoices(BaseModel):
    inv_date: str
    candidate_id: int
    period_start: str
    period_end: str
    txn_id: int
    hours_worked: float
    inv_value: float
    inv_status: str #NEWLY_SUBMITTED >> PROCESSED >> PAID


# Connect to SQLite database
def connectDB():
    conn = sqlite3.connect('hired.db')
    return conn.cursor(), conn

#Authentication functions
# Function to hash passwords
def get_password_hash(password: str):
    #Generate a SHA-256 hash of the input password.    - password: str, the plain text password to be hashed
    password_bytes = password.encode('utf-8')
    hash_obj = hashlib.sha256()
    hash_obj.update(password_bytes)
    hashed_password = hash_obj.hexdigest()
    return hashed_password

# Function to verify passwords
def verify_password(plain_password, hashed_password):
    #     Verify if a plain text password matches the hashed password.
    hashed_input_password = get_password_hash(plain_password)
    print("plain, hashinput, newhash tryhash", plain_password, hashed_password, hashed_input_password, get_password_hash(SECRET_KEY), SECRET_KEY)
    if hashed_input_password == hashed_password:
        return True
    else:
        return False


# Function to generate access token
def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to authenticate users
def authenticate_user(username: str, password: str):
    user_data = find_user_by_name(username)
    print('auth ', user_data[1], user_data[5])
    if user_data:
        if verify_password(password, user_data[5]):
            return user_data[1]
    return None

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

# Function to handle new invoice creation
@app.post("/new_invoice")
def create_invoice(invoice: Invoices):
    save_data('invoices', invoice.dict())
    return {"message": "Invoice created successfully"}

# Function to handle new invoice creation
@app.post("/new_user")
def create_user(user: Users):
    save_data('users', user.dict())
    return {"message": "User created successfully"}

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

# Function to list all invoices
@app.get("/list_invoices")
def list_invocies():
    return get_all_records('invoices')

# Function to list all invoices
@app.get("/list_users")
def list_users():
    return get_all_records('users')

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

# Function to update a invoice
@app.put("/update_invoice/{invoice_id}")
def update_invoice(invoice_id: int, invoice: Invoices):
    update_data('invoices', invoice_id, invoice.dict())
    return {"message": "Invoice updated successfully"}

# Function to update a invoice
@app.put("/update_user/{user_id}")
def update_user(user_id: int, user: Users):
    update_data('users', user_id, user.dict())
    return {"message": "User updated successfully"}

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

# Function to find a invoice by ID
@app.get("/find_invoice/{invoice_id}")
def find_invoice(invoice_id: int):
    invoice = find_record_by_id('invoices', invoice_id)
    if invoice:
        return invoice
    else:
        raise HTTPException(status_code=404, detail="Invoice not found")

# Function to find a invoice by ID
@app.get("/find_user/{user_id}")
def find_user(user_id: int):
    user = find_record_by_id('users', user_id)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
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

# Function to find a user by name
@app.get("/find_user_by_name/{user_name}")
def find_user_by_name(user_name: str):
    user = find_record_by_name('users', user_name)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
# Authenticataion functions
# Function to generate access token route
@app.post("/generate_token")
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user[1]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Function to verify token route
@app.post("/verify_token")
async def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_name: str = payload.get("sub")
    if user_name is None:
        raise credentials_exception
    #token_data = TokenData(username=user_name)
    return token

# Authenticataion functions
@app.post("/authenticate")
async def authenticate(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user[1]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Authentication functions
#Function to create new DB
@app.get("/create_db")
def createDB():
    conn = sqlite3.connect('hired.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
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
            name TEXT UNIQUE,
            client_mgr TEXT,
            payment_freq TEXT,
            client_type TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inv_date TEXT,
            candidate_id INTEGER,
            period_start TEXT,
            period_end TEXT,
            txn_id INTEGER,
            hours_worked FLOAT,
            inv_value FLOAT,
            inv_status TEXT
            )
        ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            txn_date TEXT,
            candidate_id INTEGER,
            client_id INTEGER,
            recruiter_id INTEGER,
            referral_id INTEGER,
            client_price REAL,
            referral_price REAL,
            recruiter_price REAL,
            start_date TEXT,
            end_date TEXT,
            num_payments_received INTEGER,
            total_client_recv REAL,
            total_recruiter_paid REAL,
            total_referral_paid REAL,
            last_payment_date TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            email TEXT,
            msg_id str,
            role TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    return "create_db OK"



# Function to preloadDB
@app.get("/preload_db")
def preloadDB():
    candidate_data = {
        "name": "Siva Pandeti",
        "role": "Data Engineer",
        "location": "City",
        "candidate_cost": 100,
        "phone": "123-456-7890",
        "email": "john.doe@example.com",
        "feedback": "Positive",
        "cv_link": "https://example.com/johndoe_cv.pdf",
        "status": "Hired"
    }
    save_data('candidates', candidate_data)

    # cashflow_data = {
    #     "cf_date": "2022-01-15",
    #     "pay_from_id": 1,
    #     "pay_to_id": 2,
    #     "cf_value": 5000.00,
    #     "txn_id": 1,
    #     "balance": 15000.00
    # }
    # save_data('cashflows', cashflow_data)

    client_data = {
        "name": "Rayze",
        "client_mgr": "JC",
        "payment_freq": "Monthly",
        "client_type": "Owner"
    }
    save_data('clients', client_data)

    client_data = {
        "name": "TechRakers",
        "client_mgr": "Ravi Kumar",
        "payment_freq": "Monthly",
        "client_type": "Recruiter"
    }
    save_data('clients', client_data)
    client_data = {
        "name": "Sodexo",
        "client_mgr": "Martin Ng",
        "payment_freq": "Monthly",
        "client_type": "Client"
    }
    save_data('clients', client_data)
    client_data = {
        "name": "Aventar",
        "client_mgr": "Sarosh Mistry",
        "payment_freq": "Monthly",
        "client_type": "Referral"
    }
    save_data('clients', client_data)

    transaction_data = {
        "txn_date" : "2023-12-27",
        "candidate_id" : 1,
        "client_id" : 2,
        "recruiter_id" : 3,
        "referral_id" : 4,
        "client_price" : 105.0,
        "referral_price" : 2.5,
        "recruiter_price" : 100.0,
        "start_date": "2023-12-27",
        "end_date" : "2024-5-27",
        "num_payments_received" : 0,
        "total_client_recv" : 0,
        "total_recruiter_paid" : 0.0,
        "total_referral_paid" : 0.0,
        "last_payment_date" : "NULL"
    }
    save_data('transactions', transaction_data)

    invoice_data = {
        "inv_date":  "2023-12-31",
        "candidate_id": 1,
        "period_start":  "2023-12-18",
        "period_end": "2023-12-31",
        "txn_id": 1,
        "hours_worked": 72,
        "inv_value":  7560,
        "inv_status": "PROCESSED" #NEWLY_SUBMITTED >> PROCESSED >> PAID
    }
    save_data('invoices', invoice_data)

    user_data = {
        "name": "JC",
        "email": "212cooperja@gmail.com",
        "msg_id": "@jc212",
        "role": "ADMIN",
        "password": get_password_hash(SECRET_KEY)
    }
    save_data('users', user_data)

    ##########
    authenticated_token = auth_test("JC", "adfaa")
    if authenticated_token:
        print("Authenticated. Token:", authenticated_token)
    else:
        print("Authentication failed.")
    ################

    return "preload_db OK"

## TEST AUTH
async def auth_test(username: str, password: str):
    # Step 1: Generate token
    token_response = await generate_token(username=username, password=password)
    
    # Step 2: Check if authentication succeeded
    if token_response.get("access_token"):
        return token_response.get("access_token")
    else:
        # Step 3: If authentication fails, try to authenticate directly
        authenticate_response = await authenticate(username=username, password=password)
        if authenticate_response.get("access_token"):
            return authenticate_response.get("access_token")
        else:
            return None
        


## TEST AUTH


##MAIN
if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI server using uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
