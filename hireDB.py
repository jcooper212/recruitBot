
#1 send audio and transcribe to text
#2 send to chatgpt and get response
#3 save chat history and send back n forth


from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import openai
import os
import json
import requests


app = FastAPI()

class Candidate(BaseModel):
    id: int
    Name: str
    Role: str
    Location: str
    Cost: float
    Client_Price: float
    Phone: str
    Email: str
    Feedback: Optional[str] = None
    CV: Optional[str] = None
    Status: str
    Client: Optional[str] = None
    Hired_Rate: Optional[float] = None
    Manager: Optional[str] = None

# In-memory database (replace with a real database in a production scenario)
candidates_db = []

@app.get("/")
def read_root():
    return {"Hello": "Amazing"}

@app.post("/candidates/", response_model=Candidate)
def create_candidate(candidate: Candidate):
    candidates_db.append(candidate)
    return candidate

@app.get("/candidates/", response_model=List[Candidate])
def read_candidates(skip: int = 0, limit: int = 10):
    return candidates_db[skip : skip + limit]

@app.get("/candidates/{candidate_id}", response_model=Candidate)
def read_candidate(candidate_id: int):
    candidate = next((c for c in candidates_db if c.id == candidate_id), None)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate

@app.put("/candidates/{candidate_id}", response_model=Candidate)
def update_candidate(candidate_id: int, updated_candidate: Candidate):
    candidate = next((c for c in candidates_db if c.id == candidate_id), None)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    candidate_dict = candidate.dict()
    updated_dict = updated_candidate.dict()

    for key, value in updated_dict.items():
        if value is not None:
            candidate_dict[key] = value

    candidates_db[candidate_id - 1] = Candidate(**candidate_dict)
    return candidates_db[candidate_id - 1]

@app.delete("/candidates/{candidate_id}", response_model=Candidate)
def delete_candidate(candidate_id: int):
    candidate = next((c for c in candidates_db if c.id == candidate_id), None)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    candidates_db.remove(candidate)
    return candidate


########