
#1 send audio and transcribe to text
#2 send to chatgpt and get response
#3 save chat history and send back n forth


from fastapi import FastAPI, UploadFile
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import openai
import os
import json
import requests

load_dotenv()
openai.api_key = os.getenv("OPEN_AI_KEY")
openai.organization = os.getenv("OPEN_AI_ORG")
elevenlabs_key = os.getenv("ELEVENLABS_KEY")

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

##Built for audio
@app.post("/talk")
async def post_audio(file: UploadFile):
    user_message = transcribe_audio(file)
    chat_response = get_chat_response(user_message)
    audio_output = text_to_speech(chat_response)

    def iterfile():
        yield audio_output
    return StreamingResponse(iterfile(), media_type="audio/mpeg")


##Built for telegram chat
@app.post("/chat")
async def post_chat(user_message: str):
    print(user_message)
    chat_response = get_chat_response(user_message)
    print(chat_response)
    return chat_response

#Functions for Talk
def transcribe_audio(file):
    audio_file = open(file.filename, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    #transcript = {"role": "user", "content": "What is Ethereum"}
    print(transcript)
    return transcript

#interact with OpenAI send mesage with history and get response
def get_chat_response(user_message):
    messages = load_messages()
    if type(user_message) == str:
        messages.append({"role": "user", "content": user_message})
    else:
        messages.append({"role": "user", "content": user_message['text']})

    gpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    parsed_gpt_response = gpt_response['choices'][0]['message']['content']
    print(gpt_response)

    if type(user_message) == str:
        save_messages(user_message,parsed_gpt_response)
    else:
        save_messages(user_message['text'],parsed_gpt_response)
    return parsed_gpt_response

#load all json messages from database
def load_messages():
    messages = []
    file = "database.json"

    empty = os.stat(file).st_size == 0
    if not empty:
        with open(file) as db_file:
            data = json.load(db_file)
            for item in data:
                messages.append(item)
    else:
        messages.append(
            {"role": "system", "content": "You are interviewing the user for a Python senior developer position. Ask 10 interactive questions. At the end return back with a score. Your name is Joby. The user is Jay. Keep responses under 30 words and be concise and professional"}
        )
    return messages

#save messages to database
def save_messages(user_message, gpt_response):
    file = 'database.json'
    messages = load_messages()
    messages.append({"role": "user", "content": user_message})
    messages.append({"role": "assistant", "content": gpt_response})

    with open(file, "w") as f:
        json.dump(messages, f)

def text_to_speech(text):
    voice_id = "pNInz6obpgDQGcFmaJgB"

    body = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0,
            "style": 0.5,
            "use_speaker_boost": True
        }
    }
    headers = {
        "Content-Type": "application/json",
        "accept": "audio/mpeg",
        "xi-api-key": elevenlabs_key
    }
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    try:
        print(url, "\n", headers, "\n", body )
        response = requests.post(url, json=body, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            print("errrrrr")

    except Exception as e:
        print(e)

@app.post("/upload")
async def create_upload(file: UploadFile):
    return {"filename": file.filename}
