from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import jwt
import hashlib
from pydantic import BaseModel
from datetime import datetime, timedelta
from dotenv import load_dotenv
import openai
import os

from models import Base, Candidate, Client, Transaction, User, Cashflow, Invoice, ClientInvoice, get_db

# Initialize
load_dotenv()
openai.api_key = os.getenv("OPEN_AI_KEY")
openai.organization = os.getenv("OPEN_AI_ORG")

# JWT Define a secret key (change this to a secure random value in production)
SECRET_KEY = os.getenv("RAYZE_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# Allow requests from localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to hash passwords
def get_password_hash(password: str):
    password_bytes = password.encode('utf-8')
    hash_obj = hashlib.sha256()
    hash_obj.update(password_bytes)
    hashed_password = hash_obj.hexdigest()
    return hashed_password

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

# Function to list all users
@app.get("/list_users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# Authentication functions
@app.get("/create_db")
def create_db():
    return "Database initialized"

@app.get("/preload_db")
def preload_db(db: Session = Depends(get_db)):
    # Candidate data
    candidates = [
        Candidate(
            name="Siva Pandeti",
            role="Data Engineer",
            location="Virgina",
            candidate_cost=100,
            phone="703-937-7731",
            email="psivah@gmail.com",
            feedback="Positive",
            cv_link="https://drive.google.com/file/d/1jkXYMRNpgrfysYOAXDzricr0gswyy0o6/view?usp=drive_link",
            status="Hired"
        ),
        Candidate(
            name="Balachander Kandukuri",
            role="ML Engineer",
            location="Texas",
            candidate_cost=110,
            phone="346-565-5618",
            email="kbalachandra1007@gmail.com",
            feedback="Positive",
            cv_link="https://docs.google.com/document/d/1PUErMHUVJVJRXK5pKqaI-RXsCcdEB74d/edit?usp=sharing&ouid=116979632690159824360&rtpof=true&sd=true",
            status="Hired"
        ),
        Candidate(
            name="Nishant Vagasiha",
            role="Ruby on rails Engineer",
            location="India",
            candidate_cost=32,
            phone="+91  87932 93234",
            email="nishant@webmatrixcorp.com",
            feedback="Positive",
            cv_link="https://docs.google.com/document/d/18u87iGyZYepZEnMMvQWx2nxQ9SGjWR8s3peWF9dlDPc/edit?usp=sharing",
            status="Hired"
        ),
        Candidate(
            name="Mayur Mulay",
            role="QA Engineer",
            location="India",
            candidate_cost=30,
            phone="+91 9404406545",
            email="mayurkmulay91@gmail.com",
            feedback="Positive",
            cv_link="https://docs.google.com/document/d/12JQITOn0FfmoAkkTBbh8cZXskCur_6Ekw0vvQZPZGXI/edit?usp=sharing",
            status="Hired"
        ),
        Candidate(
            name="Iti Behati",
            role="QA Engineer",
            location="USA",
            candidate_cost=69,
            phone="+1 240 889 9419",
            email="bahetyiti@gmail.com",
            feedback="Positive",
            cv_link="https://docs.google.com/document/d/1jKs2Bd_eleFrvm4VmUmXPgfAhjFDtnf5qUrC2hMgkIg/edit?usp=sharing",
            status="Hired"
        ),
        Candidate(
            name="Hani Kitabwalla",
            role="Data Analyst",
            location="USA",
            candidate_cost=44,
            phone="+1 610 390 7990",
            email="hkitab08@gmail.com",
            feedback="Positive",
            cv_link="https://docs.google.com/document/d/1EG16MBzwWZ64p4xo9UhhXKNAJuuqaHCLiVQq8SsUwhY/edit?usp=sharing",
            status="Hired"
        )
    ]
    db.bulk_save_objects(candidates)
    db.commit()

    # Client data
    clients = [
        Client(
            name="Rayze",
            client_mgr="JC",
            client_email="jc@rayze.xyz",
            client_addr="21 Sycamore Drive, Roslyn NY 11576",
            client_phone="516 800 2548",
            payment_freq="Monthly",
            client_type="Owner"
        ),
        Client(
            name="TechRakers",
            client_mgr="Ravi Kumar",
            client_email="shanker@techrakers.com",
            client_addr="1602 W Pinhook Rd, Suite 202-B, Lafayette, LA  70508",
            client_phone="703 981 6261",
            payment_freq="Monthly",
            client_type="Recruiter"
        ),
        Client(
            name="Sodexo",
            client_mgr="Martin Ng",
            client_email="martin.ng@sodexo.com",
            client_addr="5290 california ave, Irvine CA 92617",
            client_phone="714-944-3542",
            payment_freq="Monthly",
            client_type="Client"
        ),
        Client(
            name="Aventar",
            client_mgr="Sarosh Mistry",
            client_email="saroshmistry@sodexo.com",
            client_addr="349 Pinebrook drive, Laguna CA 92654",
            client_phone="949 212 9927",
            payment_freq="Monthly",
            client_type="Referral"
        ),
        Client(
            name="InKind",
            client_mgr="Dijoy Divakar",
            client_email="ap@inkind.com",
            client_addr="600 Congress Ave, Suite 1700, Austin, TX 78701",
            client_phone="870-273-8473",
            payment_freq="Monthly",
            client_type="Client"
        )
    ]
    db.bulk_save_objects(clients)
    db.commit()

    # Transaction data
    transactions = [
        Transaction(
            txn_date=datetime.strptime("2023-12-26", "%Y-%m-%d").date(),
            candidate_id=1,
            client_id=3,
            recruiter_id=2,
            referral_id=4,
            client_price=105.0,
            referral_price=2.5,
            recruiter_price=100.0,
            start_date=datetime.strptime("2023-12-26", "%Y-%m-%d").date(),
            end_date=datetime.strptime("2024-06-26", "%Y-%m-%d").date(),
            num_payments_received=0,
            total_client_recv=0,
            total_recruiter_paid=0.0,
            total_referral_paid=0.0,
            last_payment_date=None
        ),
        Transaction(
            txn_date=datetime.strptime("2024-03-01", "%Y-%m-%d").date(),
            candidate_id=2,
            client_id=3,
            recruiter_id=2,
            referral_id=4,
            client_price=120.0,
            referral_price=5.0,
            recruiter_price=110.0,
            start_date=datetime.strptime("2024-03-01", "%Y-%m-%d").date(),
            end_date=datetime.strptime("2024-08-31", "%Y-%m-%d").date(),
            num_payments_received=0,
            total_client_recv=0,
            total_recruiter_paid=0.0,
            total_referral_paid=0.0,
            last_payment_date=None
        ),
        Transaction(
            txn_date=datetime.strptime("2024-03-01", "%Y-%m-%d").date(),
            candidate_id=3,
            client_id=5,
            recruiter_id=2,
            referral_id=4,
            client_price=37.0,
            referral_price=2.5,
            recruiter_price=32.0,
            start_date=datetime.strptime("2024-03-01", "%Y-%m-%d").date(),
            end_date=datetime.strptime("2024-08-31", "%Y-%m-%d").date(),
            num_payments_received=0,
            total_client_recv=0,
            total_recruiter_paid=0.0,
            total_referral_paid=0.0,
            last_payment_date=None
        ),
        Transaction(
            txn_date=datetime.strptime("2024-06-01", "%Y-%m-%d").date(),
            candidate_id=4,
            client_id=5,
            recruiter_id=2,
            referral_id=4,
            client_price=35.0,
            referral_price=2.5,
            recruiter_price=30.0,
            start_date=datetime.strptime("2024-06-01", "%Y-%m-%d").date(),
            end_date=datetime.strptime("2024-12-01", "%Y-%m-%d").date(),
            num_payments_received=0,
            total_client_recv=0,
            total_recruiter_paid=0.0,
            total_referral_paid=0.0,
            last_payment_date=None
        ),
        Transaction(
            txn_date=datetime.strptime("2024-06-01", "%Y-%m-%d").date(),
            candidate_id=5,
            client_id=3,
            recruiter_id=2,
            referral_id=4,
            client_price=76.0,
            referral_price=2.5,
            recruiter_price=30.0,
            start_date=datetime.strptime("2024-06-01", "%Y-%m-%d").date(),
            end_date=datetime.strptime("2024-12-01", "%Y-%m-%d").date(),
            num_payments_received=0,
            total_client_recv=0,
            total_recruiter_paid=0.0,
            total_referral_paid=0.0,
            last_payment_date=None
        ),
        Transaction(
            txn_date=datetime.strptime("2024-07-01", "%Y-%m-%d").date(),
            candidate_id=6,
            client_id=3,
            recruiter_id=2,
            referral_id=4,
            client_price=54.0,
            referral_price=2.5,
            recruiter_price=44.0,
            start_date=datetime.strptime("2024-07-01", "%Y-%m-%d").date(),
            end_date=datetime.strptime("2025-01-01", "%Y-%m-%d").date(),
            num_payments_received=0,
            total_client_recv=0,
            total_recruiter_paid=0.0,
            total_referral_paid=0.0,
            last_payment_date=None
        )
    ]
    db.bulk_save_objects(transactions)
    db.commit()

    # User data
    users = [
        User(
            name="jc@rayze.xyz",
            email="jc@rayze.xyz",
            msg_id="@jc212",
            role="ADMIN",
            password=get_password_hash(SECRET_KEY),
            client_id=0
        ),
        User(
            name="shanker@techrakers.com",
            email="shanker@techrakers.com",
            msg_id="@shankerravi",
            role="Recruiter",
            password=get_password_hash(CLIENT_KEY),
            client_id=0
        ),
        User(
            name="ar@techrakers.com",
            email="ar@techrakers.com",
            msg_id="@arrakers",
            role="Recruiter",
            password=get_password_hash(CLIENT_KEY),
            client_id=0
        )
    ]
    db.bulk_save_objects(users)
    db.commit()
    return "preload_db OK"

# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8800)

