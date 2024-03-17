#each candidate is either Active, Inactive (no fit), Unscreened (not interviewed)
#feedback is Positive, Negative, NoFit
#to calculate PNL only active candidates matter
candidate_data = {
    "name": "Siva Pandeti",
    "role": "Data Engineer",
    "location": "Virginia",
    "candidate_cost": 100.0,
    "phone": "123-456-7890",
    "email": "john.doe@example.com",
    "feedback": "Positive",
    "cv_link": "https://example.com/johndoe_cv.pdf",
    "status": "Active"
}
save_data('candidates', candidate_data)

#pay_from_id is the client_id. Client id = 1 means Rayze.
#each cashflow has to be associated to a transaction
#each cashflow will change the balance if Rayze is paying or recieving
cashflow_data = {
    "cf_date": "2022-01-15",
    "pay_from_id": 1,
    "pay_to_id": 2,
    "cf_value": 5000.00,
    "txn_id": 1,
    "balance": 15000.00
}
save_data('cashflows', cashflow_data)

#each client is either a Enterprise, Recruiter, Client, Intro
client_data = [
    {
    "name": "Rayze",
    "client_mgr": "JC",
    "payment_freq": "Monthly",
    "client_type": "Enterprise"
    },
    {
    "name": "TechRakers",
    "client_mgr": "Ravi Shankar",
    "payment_freq": "Monthly",
    "client_type": "Recruiter"
    },
    {
    "name": "Sodexo",
    "client_mgr": "Martin Ng",
    "payment_freq": "Monthly",
    "client_type": "Client"
    },
    {
    "name": "Aventar",
    "client_mgr": "SM",
    "payment_freq": "Monthly",
    "client_type": "Intro"
    },
    {
    "name": "InKind",
    "client_mgr": "Brian Crow",
    "payment_freq": "Monthly",
    "client_type": "Client"
    }]
save_data('clients', client_data)

transaction_data = {
    "client_id": 3,
    "client_price": 105,
    "intro_fee": 2.5,
    "intro_id": 4,
    "recruiter_price": 100,
    "recruiter_id": 2,
    "candidate_id": 1,
    "start_date": "2023-12-27",
    "end_date": "2024-05-26",
    "num_payments_received": 0,
    "total_client_invoiced": 0.00,
    "total_client_paid": 0.00,
    "total_recruiter_paid": 0.00,
    "total_intro_paid": 0.00,
    "last_payment_date": "2022-12-15"
}
