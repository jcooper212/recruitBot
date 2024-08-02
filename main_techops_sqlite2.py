from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from passlib.context import CryptContext
import jwt
import hashlib
from pydantic import BaseModel
from datetime import datetime, timedelta
from dotenv import load_dotenv
import openai
import os

# Initialize
load_dotenv()
openai.api_key = os.getenv("OPEN_AI_KEY")
openai.organization = os.getenv("OPEN_AI_ORG")

# JWT Define a secret key (change this to a secure random value in production)
SECRET_KEY = os.getenv("RAYZE_KEY")
CLIENT_KEY = os.getenv("CLIENT_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

# Allow requests from localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLAlchemy setup
DB_URL = os.getenv("DB_URL")
username = 'postgres.tmqcprxidpcefgegkczt'
host = 'aws-0-us-east-1.pooler.supabase.com'
port = '6543'
dbname = 'postgres'
db2 = f"postgresql://{username}:{password}@{host}:{port}/{dbname}"
DATABASE_URL2 = 'postgresql+psycopg2://: host=aws-0-us-east-1.pooler.supabase.com port=6543 dbname=postgres'
engine = create_engine(db2)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Drops
# drop table candidates cascade;
# drop table clients cascade;
# drop table transactions cascade;
# drop table invoices cascade;
# drop table client_invoices cascade;
# drop table cashflows cascade;
# drop table users cascade;


# Define models
class Candidate(Base):
    __tablename__ = 'candidates'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    role = Column(String)
    location = Column(String)
    candidate_cost = Column(Float)
    phone = Column(String)
    email = Column(String)
    feedback = Column(String)
    cv_link = Column(String)
    status = Column(String)

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    client_mgr = Column(String)
    client_email = Column(String)
    client_addr = Column(String)
    client_phone = Column(String)
    payment_freq = Column(String)
    client_type = Column(String)

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True, index=True)
    txn_date = Column(DateTime)
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    client_id = Column(Integer, ForeignKey('clients.id'))
    recruiter_id = Column(Integer)
    referral_id = Column(Integer)
    client_price = Column(Float)
    referral_price = Column(Float)
    recruiter_price = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    num_payments_received = Column(Integer)
    total_client_recv = Column(Float)
    total_recruiter_paid = Column(Float)
    total_referral_paid = Column(Float)
    last_payment_date = Column(DateTime)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    email = Column(String)
    msg_id = Column(String)
    role = Column(String)
    password = Column(String)
    client_id = Column(Integer)

class Cashflow(Base):
    __tablename__ = 'cashflows'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cf_date = Column(String)
    pay_from_id = Column(Integer)
    pay_to_id = Column(Integer)
    cf_value = Column(Float)
    txn_id = Column(Integer)
    balance = Column(Float)

class Invoice(Base):
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    inv_date = Column(String)
    candidate_id = Column(Integer)
    period_start = Column(String)
    period_end = Column(String)
    txn_id = Column(Integer)
    hours_worked = Column(Float)
    inv_value = Column(Float)
    inv_status = Column(String)

class ClientInvoice(Base):
    __tablename__ = 'client_invoices'
    id = Column(Integer, primary_key=True, autoincrement=True)
    inv_date = Column(String)
    due_date = Column(String)
    period_start = Column(String)
    period_end = Column(String)
    client_id = Column(Integer)
    client_name = Column(String)
    client_contact = Column(String)
    client_email = Column(String)
    client_addr = Column(String)
    client_phone = Column(String)
    explain_str = Column(String)
    inv_html = Column(String)
    inv_hash = Column(String)
    inv_value = Column(Float)
    inv_status = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# List all packges
def list_installed_packages():
    packages = pkg_resources.working_set
    package_list = sorted(["%s==%s" % (i.key, i.version) for i in packages])
    return package_list

@app.get("/packages")
def get_packages():
    return list_installed_packages()


# Function to hash passwords
def get_password_hash(password: str):
    password_bytes = password.encode('utf-8')
    hash_obj = hashlib.sha256()
    hash_obj.update(password_bytes)
    hashed_password = hash_obj.hexdigest()
    return hashed_password

# Function to verify passwords
def verify_password(plain_password, hashed_password):
    #     Verify if a plain text password matches the hashed password.
    hashed_input_password = get_password_hash(plain_password)
    print("plain input : ", plain_password, "hashed input: ", hashed_password, "hashOfPlain :", hashed_input_password, "hashOfKey: ",get_password_hash(SECRET_KEY),"key: ", SECRET_KEY)
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
def save_data(db, model, data):
    try:
        db_item = model(**data)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
    except SQLAlchemyError as e:
        db.rollback()
        print(f"An error occurred: {str(e)}")

# Function to get all records from a table
def get_all_records(table_name):
    session = SessionLocal()
    try:
        table = Table(table_name, metadata, autoload_with=engine)
        results = session.execute(table.select()).fetchall()
        return results
    except SQLAlchemyError as e:
        print(f"Error fetching records: {e}")
    finally:
        session.close()

# Function to update data in the database
def update_data(table_name, record_id, data):
    session = SessionLocal()
    try:
        table = Table(table_name, metadata, autoload_with=engine)
        update_values = {key: value for key, value in data.items()}
        session.execute(
            table.update().where(table.c.id == record_id).values(update_values)
        )
        session.commit()
    except SQLAlchemyError as e:
        print(f"Error updating data: {e}")
    finally:
        session.close()

# Function to find a record by ID
def find_record_by_id(table_name, record_id):
    session = SessionLocal()
    try:
        table = Table(table_name, metadata, autoload_with=engine)
        result = session.execute(table.select().where(table.c.id == record_id)).fetchone()
        return result
    except SQLAlchemyError as e:
        print(f"Error finding record by ID: {e}")
    finally:
        session.close()

# Function to find a record by field
def find_record_by_field(table_name, field_name, field_value):
    session = SessionLocal()
    try:
        table = Table(table_name, metadata, autoload_with=engine)
        result = session.execute(table.select().where(table.c[field_name] == field_value)).fetchall()
        return result
    except SQLAlchemyError as e:
        print(f"Error finding record by field: {e}")
    finally:
        session.close()

# Function to find a record by name
def find_record_by_name(table_name, name):
    session = SessionLocal()
    try:
        table = Table(table_name, metadata, autoload_with=engine)
        result = session.execute(table.select().where(table.c.name == name)).fetchone()
        return result
    except SQLAlchemyError as e:
        print(f"Error finding record by name: {e}")
    finally:
        session.close()


@app.get("/get_client_transactions/{recruiter_id}")
def get_client_transactions(recruiter_id: int, db: Session = Depends(get_db)):
    transactions = (
        db.query(Transaction)
        .join(Client, Transaction.client_id == Client.id)
        .join(Candidate, Transaction.candidate_id == Candidate.id)
        .filter(Transaction.recruiter_id == recruiter_id)
        .all()
    )
    return transactions

# Function to handle new candidate creation
@app.post("/new_candidate", response_model=Candidate)
def create_candidate(candidate: Candidate, db: Session = Depends(get_db)):
    candidate_data = Candidate(**candidate.dict())
    db.add(candidate_data)
    db.commit()
    db.refresh(candidate_data)
    return candidate_data

# Function to handle new client creation
@app.post("/new_client")
def create_client(client: Client, db: Session = Depends(get_db)):
    client_data = Client(**client.dict())
    db.add(client_data)
    db.commit()
    db.refresh(client_data)
    return {"message": "Client created successfully"}

# Function to handle new transaction creation
@app.post("/new_transaction")
def create_transaction(transaction: Transaction, db: Session = Depends(get_db)):
    transaction_data = Transaction(**transaction.dict())
    db.add(transaction_data)
    db.commit()
    db.refresh(transaction_data)
    return {"message": "Transaction created successfully"}

# Function to handle new cashflow creation
@app.post("/new_cashflow")
def create_cashflow(cashflow: Cashflow, db: Session = Depends(get_db)):
    cashflow_data = Cashflow(**cashflow.dict())
    db.add(cashflow_data)
    db.commit()
    db.refresh(cashflow_data)
    return {"message": "Cashflow created successfully"}

# Function to handle new invoice creation
@app.post("/new_invoice")
def create_invoice(invoice: Invoice, db: Session = Depends(get_db)):
    invoice_data = Invoice(**invoice.dict())
    db.add(invoice_data)
    db.commit()
    db.refresh(invoice_data)
    return {"message": "Invoice created successfully"}

# Function to handle new client invoice creation
@app.post("/new_client_invoice")
def create_client_invoice(invoice: ClientInvoice, db: Session = Depends(get_db)):
    client_invoice_data = ClientInvoice(**invoice.dict())
    db.add(client_invoice_data)
    db.commit()
    db.refresh(client_invoice_data)
    return {"message": "Client Invoice created successfully"}

# Function to handle new user creation
@app.post("/new_user")
def create_user(user: User, db: Session = Depends(get_db)):
    user_data = User(**user.dict())
    db.add(user_data)
    db.commit()
    db.refresh(user_data)
    return {"message": "User created successfully"}

# Function to list all candidates
@app.get("/list_candidates")
def list_candidates(db: Session = Depends(get_db)):
    candidates = db.query(Candidate).all()
    return candidates

# Function to list all clients
@app.get("/list_clients")
def list_clients(db: Session = Depends(get_db)):
    clients = db.query(Client).all()
    return clients

# Function to list all transactions
@app.get("/list_transactions")
def list_transactions(db: Session = Depends(get_db)):
    transactions = db.query(Transaction).all()
    return transactions

# Function to list all cashflows
@app.get("/list_cashflows")
def list_cashflows(db: Session = Depends(get_db)):
    cashflows = db.query(Cashflow).all()
    return cashflows

# Function to list all invoices
@app.get("/list_invoices")
def list_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    return invoices

# Function to list all client invoices
@app.get("/list_client_invoices")
def list_client_invoices(db: Session = Depends(get_db)):
    client_invoices = db.query(ClientInvoice).all()
    return client_invoices

# Function to list all users
@app.get("/list_users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# Function to update a candidate
@app.put("/update_candidate/{candidate_id}")
def update_candidate(candidate_id: int, candidate: CandidateUpdate, db: Session = Depends(get_db)):
    candidate_to_update = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate_to_update:
        raise HTTPException(status_code=404, detail="Candidate not found")

    for key, value in candidate.dict().items():
        setattr(candidate_to_update, key, value)
    
    db.commit()
    db.refresh(candidate_to_update)
    return {"message": "Candidate updated successfully"}

# Function to update a client
@app.put("/update_client/{client_id}")
def update_client(client_id: int, client: ClientUpdate, db: Session = Depends(get_db)):
    client_to_update = db.query(Client).filter(Client.id == client_id).first()
    if not client_to_update:
        raise HTTPException(status_code=404, detail="Client not found")

    for key, value in client.dict().items():
        setattr(client_to_update, key, value)
    
    db.commit()
    db.refresh(client_to_update)
    return {"message": "Client updated successfully"}

# Function to update a transaction
@app.put("/update_transaction/{transaction_id}")
def update_transaction(transaction_id: int, transaction: TransactionUpdate, db: Session = Depends(get_db)):
    transaction_to_update = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction_to_update:
        raise HTTPException(status_code=404, detail="Transaction not found")

    for key, value in transaction.dict().items():
        setattr(transaction_to_update, key, value)
    
    db.commit()
    db.refresh(transaction_to_update)
    return {"message": "Transaction updated successfully"}

# Function to update a cashflow
@app.put("/update_cashflow/{cashflow_id}")
def update_cashflow(cashflow_id: int, cashflow: CashflowUpdate, db: Session = Depends(get_db)):
    cashflow_to_update = db.query(Cashflow).filter(Cashflow.id == cashflow_id).first()
    if not cashflow_to_update:
        raise HTTPException(status_code=404, detail="Cashflow not found")

    for key, value in cashflow.dict().items():
        setattr(cashflow_to_update, key, value)
    
    db.commit()
    db.refresh(cashflow_to_update)
    return {"message": "Cashflow updated successfully"}

# Function to update an invoice
@app.put("/update_invoice/{invoice_id}")
def update_invoice(invoice_id: int, invoice: InvoiceUpdate, db: Session = Depends(get_db)):
    invoice_to_update = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice_to_update:
        raise HTTPException(status_code=404, detail="Invoice not found")

    for key, value in invoice.dict().items():
        setattr(invoice_to_update, key, value)
    
    db.commit()
    db.refresh(invoice_to_update)
    return {"message": "Invoice updated successfully"}

# Function to update a client invoice
@app.put("/update_client_invoice/{invoice_id}")
def update_client_invoice(invoice_id: int, invoice: ClientInvoiceUpdate, db: Session = Depends(get_db)):
    client_invoice_to_update = db.query(ClientInvoice).filter(ClientInvoice.id == invoice_id).first()
    if not client_invoice_to_update:
        raise HTTPException(status_code=404, detail="Client Invoice not found")

    for key, value in invoice.dict().items():
        setattr(client_invoice_to_update, key, value)
    
    db.commit()
    db.refresh(client_invoice_to_update)
    return {"message": "Client Invoice updated successfully"}

# Function to update a user
@app.put("/update_user/{user_id}")
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    user_to_update = db.query(User).filter(User.id == user_id).first()
    if not user_to_update:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user.dict().items():
        setattr(user_to_update, key, value)
    
    db.commit()
    db.refresh(user_to_update)
    return {"message": "User updated successfully"}

@app.get("/find_candidate/{candidate_id}")
def find_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if candidate:
        return candidate
    else:
        raise HTTPException(status_code=404, detail="Candidate not found")

# Function to find a client by ID
@app.get("/find_client/{client_id}")
def find_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if client:
        return client
    else:
        raise HTTPException(status_code=404, detail="Client not found")

# Function to find a transaction by ID
@app.get("/find_transaction/{transaction_id}")
def find_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction:
        return transaction
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")

# Function to find a cashflow by ID
@app.get("/find_cashflow/{cashflow_id}")
def find_cashflow(cashflow_id: int, db: Session = Depends(get_db)):
    cashflow = db.query(Cashflow).filter(Cashflow.id == cashflow_id).first()
    if cashflow:
        return cashflow
    else:
        raise HTTPException(status_code=404, detail="Cashflow not found")

# Function to find an invoice by ID
@app.get("/find_invoice/{invoice_id}")
def find_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if invoice:
        return invoice
    else:
        raise HTTPException(status_code=404, detail="Invoice not found")

# Function to find a client invoice by ID
@app.get("/find_client_invoice/{invoice_id}")
def find_client_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(ClientInvoice).filter(ClientInvoice.id == invoice_id).first()
    if invoice:
        return invoice
    else:
        raise HTTPException(status_code=404, detail="Client Invoice not found")

# Function to find a client invoice by client ID
@app.get("/find_invoice_client_id/{client_id}")
def find_invoice_by_client_id(client_id: int, db: Session = Depends(get_db)):
    invoices = db.query(ClientInvoice).filter(ClientInvoice.client_id == client_id).all()
    if invoices:
        return invoices
    else:
        raise HTTPException(status_code=404, detail="Client Invoices not found")

# Function to find a user by ID
@app.get("/find_user/{user_id}")
def find_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")

# Function to find a candidate by name
@app.get("/find_candidate_by_name/{name}")
def find_candidate_by_name(name: str, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).filter(Candidate.name == name).first()
    if candidate:
        return candidate
    else:
        raise HTTPException(status_code=404, detail="Candidate not found")

# Function to find a user by name
@app.get("/find_user_by_name/{user_name}")
def find_user_by_name(user_name: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == user_name).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")

# Function to find transactions for a given client ID
@app.get("/find_my_candidates/{client_id}")
def find_my_candidates(client_id: int, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter(Transaction.client_id == client_id).all()
    if transactions:
        return transactions
    else:
        raise HTTPException(status_code=404, detail="Transactions not found")

# Function to find the latest invoice by client ID
@app.get("/find_latest_invoice/{client_id}")
def find_latest_invoice(client_id: str, db: Session = Depends(get_db)):
    latest_invoice = db.query(ClientInvoice.inv_date, func.max(ClientInvoice.id))\
                       .filter(ClientInvoice.client_id == client_id)\
                       .first()

    if latest_invoice:
        inv_date, _ = latest_invoice
        return {"inv_date": inv_date}
    else:
        raise HTTPException(status_code=404, detail="Invoice not found")

# Submit client invoice
@app.post("/submit_client_invoice")
def submit_client_invoice(invoice: ClientInvoice, db: Session = Depends(get_db)):
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    # Extract the client invoice id
    inv_id = db.query(func.max(ClientInvoice.id))\
               .filter(ClientInvoice.inv_date == invoice.inv_date,
                       ClientInvoice.client_id == invoice.client_id)\
               .scalar()

    if inv_id:
        # Update invoice HTML and hash
        invoice.inv_html = create_html_invoice(inv_id, invoice)
        invoice.inv_hash = get_password_hash(f"{inv_id}_{invoice.client_id}_{invoice.inv_date}")

        db.query(ClientInvoice)\
          .filter(ClientInvoice.id == inv_id)\
          .update({"inv_html": invoice.inv_html, "inv_hash": invoice.inv_hash})
        db.commit()

        return {"inv_html": invoice.inv_html}
    else:
        raise HTTPException(status_code=404, detail="Invoice not found")

@app.post("/generate_invoices/{transaction_id}")
def generate_invoices(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    start_date = datetime.strptime(transaction.start_date, '%Y-%m-%d')
    end_date = datetime.strptime(transaction.end_date, '%Y-%m-%d')
    num_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1

    invoices_written = 0
    for i in range(num_months):
        inv_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)  # Last day of the month
        period_start = start_date
        period_end = inv_date
        hours_worked = 160  # Default hours worked
        inv_value = transaction.client_price * hours_worked
        inv_status = "PRE"

        invoice_data = {
            "inv_date": inv_date.strftime('%Y-%m-%d'),
            "candidate_id": transaction.candidate_id,
            "period_start": period_start.strftime('%Y-%m-%d'),
            "period_end": period_end.strftime('%Y-%m-%d'),
            "txn_id": transaction.id,
            "hours_worked": hours_worked,
            "inv_value": inv_value,
            "inv_status": inv_status
        }

        new_invoice = Invoice(**invoice_data)
        db.add(new_invoice)
        db.commit()
        invoices_written += 1

        # Move start_date to the next month
        start_date = start_date + timedelta(days=32)

    return {"invoices_written": invoices_written}

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
    #print('adsf', form_data.username, form_data.password)
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

 #Register
@app.post("/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_data = {
        "name": form_data.username,
        "email": form_data.username,
        "role": "CLIENT",
        "password": get_password_hash(form_data.password),
        "client_id": 0
    }
    db.add(User(**user_data))
    db.commit()
    return {"message": "User registered successfully"}

# Get Invoice
@app.get("/get_invoice/{id_str}")
def get_invoice(id_str: str, db: Session = Depends(get_db)):
    try:
        invoice = db.execute(select(ClientInvoice.inv_html).filter(ClientInvoice.inv_hash == id_str)).scalars().one()
        return {"html": invoice}
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Invoice not found")

def create_html_invoice(inv_id: int, db: Session) -> str:
    # Fetch the invoice details from the database
    invoice = db.query(ClientInvoice).filter(ClientInvoice.id == inv_id).first()
    
    if not invoice:
        raise ValueError("Invoice not found")

    # Prepare the HTML content
    path_to_template = PATH_TO_CONTENT / "invoice_template.html"
    
    # Read the template
    with open(path_to_template, 'r') as file:
        html_content = file.read()
        
        html_content = html_content.replace("total_due", f"${invoice.inv_value:,.2f}")
        html_content = html_content.replace("due_date", invoice.due_date)
        html_content = html_content.replace("invoice_title", "Technology Services")
        html_content = html_content.replace("invoice_num", str(inv_id))
        html_content = html_content.replace("invoice_date", invoice.inv_date)
        html_content = html_content.replace("client_name", invoice.client_name)
        # html_content = html_content.replace("client_contact", invoice.client_contact)
        html_content = html_content.replace("invoice_table", invoice.explain_str)
        html_content = html_content.replace("rayze_logo", RAYZE_LOGO.as_posix())
    
    # Paths for new content
    new_title = f"Inv_{invoice.client_name}_{inv_id}.html"
    new_title_pdf = f"Inv_{invoice.client_name}_{inv_id}.pdf"
    
    path_to_new_content = PATH_TO_CONTENT / new_title
    path_to_new_pdf = PATH_TO_CONTENT / new_title_pdf
    
    # Save the HTML content to a file
    with open(path_to_new_content, 'w') as file:
        file.write(html_content)
    
    # Return the path to the HTML file
    return str(path_to_new_content)



# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8800)

