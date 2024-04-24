### BOT that interviews in React

USAGE:

#source venv

source venv/bin/activate
pip install -r requirements.txt

#start server to serve up rest apis
uvicorn main:app --reload

#start telegram bot service (in a new terminal)
python getHiredBot.py


Useful things I need to do:

New Client & referral_commission
1/ Add new client - JC
2/ Add new Recruiter (or) referral - JC

Candidates & Jobs
1/ New (or) update job description with unique Job_id - JC
2/ View Job ids & Propose candidate for Job_id - Ravi

Feedback
0/ Generate Interview Q&A - JC
1/ Record Interview feedback - JC
2/ Submit candidate for Job_id - JC
5/ Update Client feedback on candidate (STATUS, FEEDBACK, etc) - JC
6/ Notify sendemail autogenerated email to Recruiter for candidate hire - JC

Hired Transactions
1/ Propose Transaction for hire & Auto-Generate Work order - Ravi
2/ Approve Transaction for hire - JC

Billing
1/ Propose Invoice for bi-weekly (or) monthly work - Ravi
2/ Approve Invoice for bi-weekly (or) monthly work & sendmail generated bill to client - JC
3/ Update Client payment status - JC
4/ Update Invoice payment status - JC




/////////////////To Do/////
Login SCreen
- Forgot password
- captch
- error checking on text fields

