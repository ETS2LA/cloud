from fastapi import Header
from env import env
import requests
import database
import fastapi
import uvicorn
import json

API_ENDPOINT = 'https://discord.com/api/v10'
CLIENT_ID = env.CLIENT_ID
CLIENT_SECRET = env.CLIENT_SECRET
REDIRECT_URI = 'http://localhost:8000/auth/discord/login'

app = fastapi.FastAPI()

def verify_token(token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    r = requests.get('%s/users/@me' % API_ENDPOINT, headers=headers)
    return r.status_code == 200

def get_user_id(token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    r = requests.get('%s/users/@me' % API_ENDPOINT, headers=headers)
    r.raise_for_status()
    return r.json()

@app.get('/auth/discord/login')
def exchange_code(code):
    print("Got code:", code)
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': 'identify'
    }
    headers = {
        'content-type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers, auth=(CLIENT_ID, CLIENT_SECRET))
    r.raise_for_status()
    print(json.dumps(r.json(), indent=4))
    user = get_user_id(r.json()['access_token'])
    print(json.dumps(user, indent=4))
    
    # Check if the user exists
    database_response = database.get_new_token(user['id'])
    if database_response.status != 200:
        database_response = database.create_user(user['id'], user['username'])
        if database_response.status != 200:
            return {'error': 'Failed to create user.'}
    
    return database_response.data

@app.get('/user/{user_id}')
def get_user(user_id: str, authorization: str = Header(None)):
    if not authorization:
        return {'error': 'No authorization header.'}
    return database.get_user(user_id, authorization)

@app.get('/heartbeat')
def heartbeat():
    return {'status': 'ok'}

@app.get('/auth/discord')
def open_login():
    return f'https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=identify'

if __name__ == '__main__':
    # open_login()
    uvicorn.run(app, host='localhost', port=8000)