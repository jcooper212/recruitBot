from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CandidateBase(BaseModel):
    name: str
    role: str
    location: str
    candidate_cost: float
    phone: str
    email: str
    feedback: Optional[str] = None
    cv_link: Optional[str] = None
    status: str

class CandidateCreate(CandidateBase):
    pass

class Candidate(CandidateBase):
    id: int

    class Config:
        orm_mode: True

class ClientBase(BaseModel):
    name: str
    client_mgr: str
    client_email: str
    client_addr: str
    client_phone: str
    payment_freq: str
    client_type: str

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int

    class Config:
        orm_mode: True

class TransactionBase(BaseModel):
    txn_date: datetime
    candidate_id: int
    client_id: int
    recruiter_id: int
    referral_id: int
    client_price: float
    referral_price: float
    recruiter_price: float
    start_date: datetime
    end_date: datetime
    num_payments_received: int
    total_client_recv: float
    total_recruiter_paid: float
    total_referral_paid: float
    last_payment_date: datetime

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int

    class Config:
        orm_mode: True

class UserBase(BaseModel):
    name: str
    email: str
    msg_id: str
    role: str
    password: str
    client_id: int

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode: True

class CashflowBase(BaseModel):
    cf_date: str
    pay_from_id: int
    pay_to_id: int
    cf_value: float
    txn_id: int
    balance: float

class CashflowCreate(CashflowBase):
    pass

class Cashflow(CashflowBase):
    id: int

    class Config:
        orm_mode: True

class InvoiceBase(BaseModel):
    inv_date: str
    candidate_id: int
    period_start: str
    period_end: str
    txn_id: int
    hours_worked: float
    inv_value: float
    inv_status: str

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: int

    class Config:
        orm_mode: True

class ClientInvoiceBase(BaseModel):
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
    inv_html: str
    inv_hash: str
    inv_value: float
    inv_status: str

class ClientInvoiceCreate(ClientInvoiceBase):
    pass

class ClientInvoice(ClientInvoiceBase):
    id: int

    class Config:
        orm_mode: True

