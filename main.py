from fastapi.middleware.cors import CORSMiddleware
from fastapi import Header
from env import env
import requests
import database
import fastapi
import uvicorn
import classes
import json

DEVELOPMENT = False
API_ENDPOINT = 'https://discord.com/api/v10'
CLIENT_ID = env.CLIENT_ID
CLIENT_SECRET = env.CLIENT_SECRET
if DEVELOPMENT:
    REDIRECT_URI = 'http://localhost:8000/auth/discord/login' # Redirect to the in app login URL
    print(f"Testing URL: https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauth%2Fdiscord%2Flogin&scope=identify")
else:
    REDIRECT_URI = 'http://localhost:37520/auth/discord/login' # Redirect to the in app login URL

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# MARK: Auth


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

@app.get('/auth/discord')
def discord_url():
    return f'https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope=identify'

@app.get('/auth/discord/login')
def exchange_code(code):
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
    user = get_user_id(r.json()['access_token'])
    
    # Check if the user exists
    database_response = database.get_new_token(user['id'])
    if database_response.status != 200:
        database_response = database.create_user(user['id'], user['username'])
        if database_response.status != 200:
            return {'error': 'Failed to create user.'}
    
    return database_response.data


# MARK: User


@app.get('/user/{user_id}')
def get_user(user_id: str, authorization: str = Header(None)):
    if not authorization:
        return {'error': 'No authorization header.'}
    return database.get_user(user_id, authorization)

@app.get('/delete/{user_id}')
def delete_user(user_id: str, authorization: str = Header(None)):
    if not authorization:
        return {'error': 'No authorization header.'}
    return database.delete_user(user_id, authorization)


# MARK: Jobs


@app.post('/user/{user_id}/job/started')
def job_started(user_id: str, job: classes.Job, authorization: str = Header(None)):
    if not authorization:
        return {'error': 'No authorization header.'}
    return database.job_started(user_id, authorization, job)

@app.post('/user/{user_id}/job/finished')
def job_finished(user_id: str, job: classes.FinishedJob, authorization: str = Header(None)):
    if not authorization:
        return {'error': 'No authorization header.'}
    return database.job_finished(user_id, authorization, job)

@app.post('/user/{user_id}/job/cancelled')
def job_cancelled(user_id: str, job: classes.CancelledJob, authorization: str = Header(None)):
    if not authorization:
        return {'error': 'No authorization header.'}
    return database.job_cancelled(user_id, authorization, job)

@app.get('/user/{user_id}/jobs')
def get_jobs(user_id: str, authorization: str = Header(None)):
    if not authorization:
        return {'error': 'No authorization header.'}
    return database.get_jobs(user_id, authorization)

# MARK: Heartbeat


@app.get('/heartbeat')
def heartbeat():
    return {'status': 'ok'}

if __name__ == '__main__':
    if DEVELOPMENT:
        print("WARNING: Running on localhost")
        uvicorn.run(app, host='localhost', port=8000)
    else:
        uvicorn.run(app, host='0.0.0.0', port=8000)