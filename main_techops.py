from fastapi import FastAPI, HTTPException
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
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
#import genInvoice
from pathlib import Path
from bs4 import BeautifulSoup as Soup

PATH_TO_BLOG = Path('/Users/jcooper/py/genAi/recruitBot')
PATH_TO_CONTENT = PATH_TO_BLOG/"content"
PATH_TO_CONTENT.mkdir(exist_ok=True, parents=True)
RAYZE_LOGO = PATH_TO_CONTENT/"rayze_logo.jpg"



#Initialize
load_dotenv()
openai.api_key = os.getenv("OPEN_AI_KEY")
openai.organization = os.getenv("OPEN_AI_ORG")
elevenlabs_key = os.getenv("ELEVENLABS_KEY")

# JWT Define a secret key (change this to a secure random value in production)
sec_value = os.getenv("RAYZE_KEY")
SECRET_KEY = str(sec_value)
sec_value = os.getenv("CLIENT_KEY")
CLIENT_KEY = str(sec_value)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
# Allow requests from localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
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
    client_email: str
    client_addr: str
    client_phone: str
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

class ClientInvoices(BaseModel):
    inv_date: str
    due_date: str
    period_start: str
    period_end: str
    client_id: int
    client_name: str
    client_contact: str
    client_email: str
    client_addr: str
    client_phone: str
    explain_str: str
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

# Function to find a record by ID
def find_record_by_field(table_name, field_name, field_value):
    cursor, conn = connectDB()
    cursor.execute(f'SELECT * FROM {table_name} WHERE {field_name} = --- ', field_value)
    print()
    return cursor.fetchall()

# Function to find a record by name
def find_record_by_name(table_name, name):
    cursor, conn = connectDB()
    cursor.execute(f'SELECT * FROM {table_name} WHERE name = ?', (name,))
    return cursor.fetchone()

#get transactions for a given recruiter
@app.get("/get_client_transactions/{recruiter_id}")
def get_client_transactions(recruiter_id):
    # Connect to the SQLite database
    cursor, conn = connectDB()

    # Execute the SQL query with parameterized input
    cursor.execute('''
        SELECT transactions.id AS txn_id, candidates.id AS candidate_id, clients.name AS client_name, candidates.name AS candidate_name,
        transactions.recruiter_price, transactions.client_price, clients.client_mgr as client_contact, clients.client_email AS client_email,
        clients.client_addr AS client_addr, clients.client_phone AS client_phone, clients.id AS client_id
        FROM transactions
        JOIN clients ON transactions.client_id = clients.id
        JOIN candidates ON transactions.candidate_id = candidates.id
        WHERE transactions.recruiter_id = ?
    ''', (recruiter_id,))  # Pass the recruiter ID as a parameter

    # Fetch all rows from the result set
    rows = cursor.fetchall()

    # Close the database connection
    conn.close()

    return rows

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
@app.post("/new_client_invoice")
def create_client_invoice(invoice: ClientInvoices):
    save_data('client_invoices', invoice.dict())
    return {"message": "Client Invoice created successfully"}

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
def list_invoices():
    return get_all_records('invoices')

# Function to list all invoices
@app.get("/list_client_invoices")
def list_client_invoices():
    return get_all_records('client_invoices')

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
@app.put("/update_client_invoice/{invoice_id}")
def update_invoice(invoice_id: int, invoice: ClientInvoices):
    update_data('client_invoices', invoice_id, invoice.dict())
    return {"message": "Client Invoice updated successfully"}

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
@app.get("/find_client_invoice/{invoice_id}")
def find_client_invoice(invoice_id: int):
    invoice = find_record_by_id('client_invoices', invoice_id)
    if invoice:
        return invoice
    else:
        raise HTTPException(status_code=404, detail="Client Invoice not found")
    
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

# Function to find a user by name
@app.get("/find_my_candidates{client_id}")
def find_my_candidates(client_id: int):
    txn = find_record_by_field('transactions', 'client_id',client_id)
    if txn:
        return txn
    else:
        raise HTTPException(status_code=404, detail="Txn not found")

# Function to handle new invoice creation
@app.post("/submit_client_invoice")
def submit_client_invoice(invoice: ClientInvoices):
    save_data('client_invoices', invoice.dict()) #first save the invoice into client_invoices to get an id
    cursor, conn = connectDB()

    # Extract the client invoice id
    cursor.execute('''
        SELECT id 
        FROM client_invoices
        WHERE client_invoices.inv_date = ? AND
        client_invoices.client_id = ?
    ''', (invoice.inv_date, invoice.client_id))

    # Fetch all rows from the result set
    rows = cursor.fetchall()
    if rows:
    # Get the value from the last row
        inv_id = rows[-1][0]
    else:
        # Handle the case where no rows are returned
        inv_id = None
    # Close the database connection
    conn.close()
    #call the html creation function
    create_html_invoice(inv_id, invoice)



    
# Given a Transaction Id generate NEW temporary invoices
@app.post("/generate_invoices/{transaction_id}")
def generate_invoices(transaction_id):
    transaction = find_transaction(transaction_id)
    if not transaction:
        print("Transaction not found.")
        return 0

    # Calculate the number of invoices to be generated
    start_date = datetime.strptime(transaction[9], '%Y-%m-%d')  # Index 9 is start_date
    end_date = datetime.strptime(transaction[10], '%Y-%m-%d')  # Index 10 is end_date
    num_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1

    # Generate invoices for each end of month
    invoices_written = 0
    for i in range(num_months):
        # Calculate invoice details
        inv_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)  # Last day of month
        period_start = start_date
        period_end = inv_date
        hours_worked = 160  # Default hours worked
        inv_value = transaction[5] * hours_worked  # Index 5 is client_price
        inv_status = "PRE"

        # Insert invoice data into the database
        invoice_data = {
        "inv_date":  inv_date.strftime('%Y-%m-%d'),
        "candidate_id": transaction[2],
        "period_start":  period_start.strftime('%Y-%m-%d'),
        "period_end": period_end.strftime('%Y-%m-%d'),
        "txn_id": transaction[0],
        "hours_worked": hours_worked,
        "inv_value":  inv_value,
        "inv_status": inv_status #NEW >> PROCESSED >> PAID
        }
        save_data('invoices', invoice_data)
        invoices_written += 1
        # Move start_date to the next month
        start_date = start_date + timedelta(days=32)


        # cursor.execute('''INSERT INTO invoices (inv_date, candidate_id, period_start, period_end, txn_id, hours_worked, inv_value, inv_status) 
        #                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        #                (inv_date.strftime('%Y-%m-%d'), transaction[1], period_start.strftime('%Y-%m-%d'),
        #                 period_end.strftime('%Y-%m-%d'), transaction[0], hours_worked, inv_value, inv_status))

    
        # # Commit changes and close connection
        # conn.commit()
        # conn.close()

    return invoices_written
    
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

#create a new invoice in html
def create_html_invoice(inv_id: int, invoice: ClientInvoices):
    #new html file
    files = len(list(PATH_TO_CONTENT.glob('*.html')))
    new_title = f"Inv_{invoice.client_name}_{inv_id}.html"
    new_title_pdf = f"Inv_{invoice.client_name}_{inv_id}.pdf"

    path_to_new_content = PATH_TO_CONTENT/new_title
    path_to_new_pdf = PATH_TO_CONTENT/new_title_pdf
    path_to_template = "{}/invoice_template.html".format(PATH_TO_CONTENT)




    #read the template
    html_content=""
    with open(path_to_template, 'r') as file:
        html_content = file.read()
        html_content = html_content.replace("total_due", f"${invoice.inv_value:.2f}")
        html_content = html_content.replace("due_date", invoice.due_date)
        html_content = html_content.replace("invoice_title", "Technology Services")
        html_content = html_content.replace("invoice_num", str(inv_id))
        html_content = html_content.replace("invoice_date", invoice.inv_date)
        html_content = html_content.replace("client_name", invoice.client_name)
        html_content = html_content.replace("client_contact", invoice.client_contact)
        html_content = html_content.replace("invoice_table", invoice.explain_str)
        html_content = html_content.replace("rayze_logo", RAYZE_LOGO.as_posix())


    print("html_content is ", html_content)
    
    #Save pdf
    # Configuration for wkhtmltopdf (you might need to provide the path to the wkhtmltopdf binary)
    config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')  # Adjust path as necessary
    pdfkit.from_string(html_content, path_to_new_pdf, configuration=config)

    #write new invoice
    if not os.path.exists(path_to_new_content):
        with open(path_to_new_content,"w") as f:
            f.write(html_content)
            return path_to_new_content
    else:
        raise FileExistsError('file already exists')
    
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
            client_email TEXT,
            client_addr TEXT,
            client_phone TEXT,
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
        CREATE TABLE IF NOT EXISTS client_invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inv_date TEXT,
            due_date TEXT,
            period_start TEXT,
            period_end TEXT,
            client_id INTEGER,
            client_name TEXT,
            client_contact TEXT,
            client_email TEXT,
            client_addr TEXT,
            client_phone TEXT,
            explain_str TEXT,
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
            password TEXT,
            client_id int
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
        "location": "Virgina",
        "candidate_cost": 100,
        "phone": "703-937-7731",
        "email": "psivah@gmail.com",
        "feedback": "Positive",
        "cv_link": "https://drive.google.com/file/d/1jkXYMRNpgrfysYOAXDzricr0gswyy0o6/view?usp=drive_link",
        "status": "Hired"
    }
    save_data('candidates', candidate_data)
    candidate_data = {
        "name": "Balachander Kandukuri",
        "role": "ML Engineer",
        "location": "Texas",
        "candidate_cost": 100,
        "phone": "346-565-5618",
        "email": "kbalachandra1007@gmail.com",
        "feedback": "Positive",
        "cv_link": "https://docs.google.com/document/d/1PUErMHUVJVJRXK5pKqaI-RXsCcdEB74d/edit?usp=sharing&ouid=116979632690159824360&rtpof=true&sd=true",
        "status": "Hired"
    }
    save_data('candidates', candidate_data)
    candidate_data = {
        "name": "Nishant Vagasiha",
        "role": "Ruby on rails Engineer",
        "location": "India",
        "candidate_cost": 30,
        "phone": "+91  87932 93234",
        "email": "nishant@webmatrixcorp.com",
        "feedback": "Positive",
        "cv_link": "https://docs.google.com/document/d/18u87iGyZYepZEnMMvQWx2nxQ9SGjWR8s3peWF9dlDPc/edit?usp=sharing",
        "status": "Hired"
    }
    save_data('candidates', candidate_data)
    

    client_data = {
        "name": "Rayze",
        "client_mgr": "JC",
        "client_email": "212cooperja@gmail.com",
        "client_addr": "21 Sycamore Drive, Roslyn NY 11576",
        "client_phone": "516 800 2548",
        "payment_freq": "Monthly",
        "client_type": "Owner"
    }
    save_data('clients', client_data)

    client_data = {
        "name": "TechRakers",
        "client_mgr": "Ravi Kumar",
        "client_email": "shanker@techrakers.com",
        "client_addr": "1602 W Pinhook Rd, Suite 202-B, Lafayette, LA  70508",
        "client_phone": "703 981 6261",
        "payment_freq": "Monthly",
        "client_type": "Recruiter"
    }
    save_data('clients', client_data)
    client_data = {
        "name": "Sodexo",
        "client_mgr": "Martin Ng",
        "client_email": "martin.ng@sodexo.com",
        "client_addr": "5290 california ave, Irvine CA 92617",
        "client_phone": "714-944-3542",
        "payment_freq": "Monthly",
        "client_type": "Client"
    }
    save_data('clients', client_data)
    client_data = {
        "name": "Aventar",
        "client_mgr": "Sarosh Mistry",
        "client_email": "saroshmistry@sodexo.com",
        "client_addr": "349 Pinebrook drive, Laguna CA 92654",
        "client_phone": "949 212 9927",
        "payment_freq": "Monthly",
        "client_type": "Referral"
    }
    save_data('clients', client_data)
    client_data = {
        "name": "InKind",
        "client_mgr": "Dijoy Divakar",
        "client_email": "ap@inkind.com",
        "client_addr": "600 Congress Ave, Suite 1700, Austin, TX 78701",
        "client_phone": "870-273-8473",
        "payment_freq": "Monthly",
        "client_type": "Client"
    }
    save_data('clients', client_data)

    transaction_data = {
        "txn_date" : "2023-12-26",
        "candidate_id" : 1,
        "client_id" : 3,
        "recruiter_id" : 2,
        "referral_id" : 4,
        "client_price" : 105.0,
        "referral_price" : 2.5,
        "recruiter_price" : 100.0,
        "start_date": "2023-12-26",
        "end_date" : "2024-6-26",
        "num_payments_received" : 0,
        "total_client_recv" : 0,
        "total_recruiter_paid" : 0.0,
        "total_referral_paid" : 0.0,
        "last_payment_date" : "NULL"
    }
    save_data('transactions', transaction_data)

    transaction_data = {
        "txn_date" : "2024-03-01",
        "candidate_id" : 2,
        "client_id" : 3,
        "recruiter_id" : 2,
        "referral_id" : 4,
        "client_price" : 120.0,
        "referral_price" : 5.0,
        "recruiter_price" : 110.0,
        "start_date": "2024-03-01",
        "end_date" : "2024-08-31",
        "num_payments_received" : 0,
        "total_client_recv" : 0,
        "total_recruiter_paid" : 0.0,
        "total_referral_paid" : 0.0,
        "last_payment_date" : "NULL"
    }
    save_data('transactions', transaction_data)

    transaction_data = {
        "txn_date" : "2024-03-01",
        "candidate_id" : 3,
        "client_id" : 5,
        "recruiter_id" : 2,
        "referral_id" : 4,
        "client_price" : 37.0,
        "referral_price" : 2.5,
        "recruiter_price" : 32.0,
        "start_date": "2024-03-01",
        "end_date" : "2024-08-31",
        "num_payments_received" : 0,
        "total_client_recv" : 0,
        "total_recruiter_paid" : 0.0,
        "total_referral_paid" : 0.0,
        "last_payment_date" : "NULL"
    }
    save_data('transactions', transaction_data)

    # invoice_data = {
    #     "inv_date":  "2023-12-31",
    #     "candidate_id": 1,
    #     "period_start":  "2023-12-18",
    #     "period_end": "2023-12-31",
    #     "txn_id": 1,
    #     "hours_worked": 72,
    #     "inv_value":  7560,
    #     "inv_status": "PROCESSED" #PRE >> PROCESSED >> PAID //PRE invoices are per txn. so need to be aggregated by client
    # }
    # save_data('invoices', invoice_data)

    user_data = {
        "name": "212cooperja@gmail.com",
        "email": "212cooperja@gmail.com",
        "msg_id": "@jc212",
        "role": "ADMIN",
        "password": get_password_hash(SECRET_KEY),
        "client_id": 0
    }
    save_data('users', user_data)
    user_data = {
        "name": "shanker@techrakers.com",
        "email": "shanker@techrakers.com",
        "msg_id": "@shankerravi",
        "role": "Recruiter",
        "password": get_password_hash(CLIENT_KEY),
        "client_id": 0
    }
    save_data('users', user_data)
    user_data = {
        "name": "ar@techrakers.com",
        "email": "ar@techrakers.com",
        "msg_id": "@arrakers",
        "role": "Recruiter",
        "password": get_password_hash(CLIENT_KEY),
        "client_id": 0
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
