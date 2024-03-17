import sqlite3
import json

# Connect to SQLite database
conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS candidates (
        candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
conn.commit()

def save_candidate(candidate_data):
    # Save a candidate record to the database
    cursor.execute('''
        INSERT INTO candidates (
            name, role, location, candidate_cost, phone, email, feedback, cv_link, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        candidate_data['name'],
        candidate_data['role'],
        candidate_data['location'],
        candidate_data['candidate_cost'],
        candidate_data['phone'],
        candidate_data['email'],
        candidate_data['feedback'],
        candidate_data['cv_link'],
        candidate_data['status']
    ))
    conn.commit()

def retrieve_candidate_by_id(candidate_id):
    # Retrieve a candidate by candidate_id
    cursor.execute('SELECT * FROM candidates WHERE candidate_id = ?', (candidate_id,))
    return cursor.fetchone()

def search_candidates_by_field(field, value):
    # Search candidates by a given field
    cursor.execute(f'SELECT * FROM candidates WHERE {field} = ?', (value,))
    return cursor.fetchall()

def update_candidate_by_id(candidate_id, new_data):
    # Update a candidate by candidate_id
    cursor.execute('''
        UPDATE candidates SET
        name = ?, role = ?, location = ?, candidate_cost = ?,
        phone = ?, email = ?, feedback = ?, cv_link = ?, status = ?
        WHERE candidate_id = ?
    ''', (
        new_data['name'],
        new_data['role'],
        new_data['location'],
        new_data['candidate_cost'],
        new_data['phone'],
        new_data['email'],
        new_data['feedback'],
        new_data['cv_link'],
        new_data['status'],
        candidate_id
    ))
    conn.commit()

def delete_candidate_by_id(candidate_id):
    # Delete a candidate by candidate_id
    cursor.execute('DELETE FROM candidates WHERE candidate_id = ?', (candidate_id,))
    conn.commit()

# Example usage:
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

# Save a candidate
save_candidate(candidate_data)

# Retrieve a candidate by candidate_id
retrieved_candidate = retrieve_candidate_by_id(1)
print("Retrieved Candidate:", retrieved_candidate)

# Search candidates by a field
search_result = search_candidates_by_field("role", "Software Engineer")
print("Search Result:", search_result)

# Update a candidate by candidate_id
updated_data = {"name": "John Doe Jr.", "role": "Senior Software Engineer", "status": "Inactive"}
update_candidate_by_id(1, candidate_data)

# Retrieve the updated candidate
updated_candidate = retrieve_candidate_by_id(1)
print("Updated Candidate:", updated_candidate)

# Delete a candidate by candidate_id
delete_candidate_by_id(1)

# Confirm deletion
deleted_candidate = retrieve_candidate_by_id(1)
print("Deleted Candidate:", deleted_candidate)

# Close the database connection
conn.close()
