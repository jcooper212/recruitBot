### BOT that interviews in React
 
USAGE:

#source venv

source venv/bin/activate
pip install -r requirements.txt

#start server to serve up rest apis
uvicorn main:app --reload

#start telegram bot service (in a new terminal)
python getHiredBot.py

