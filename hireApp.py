from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

app = Flask(__name__)

API_BASE_URL = 'http://127.0.0.1:8000'  # Update with your FastAPI server URL

@app.route('/')
def index():
    candidates = requests.get(f'{API_BASE_URL}/candidates/').json()
    return render_template('index.html', candidates=candidates)

@app.route('/add_candidate', methods=['POST'])
def add_candidate():
    candidate_data = {
        'Name': request.form['Name'],
        'Role': request.form['Role'],
        'Location': request.form['Location'],
        'Cost': float(request.form['Cost']),
        'Client_Price': float(request.form['Client_Price']),
        'Phone': request.form['Phone'],
        'Email': request.form['Email'],
        'Status': request.form['Status']
    }

    response = requests.post(f'{API_BASE_URL}/candidates/', json=candidate_data)
    return redirect(url_for('index'))

@app.route('/delete_candidate/<int:candidate_id>')
def delete_candidate(candidate_id):
    requests.delete(f'{API_BASE_URL}/candidates/{candidate_id}')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

