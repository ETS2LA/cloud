import requests
from env import env
import fastapi
import uvicorn
import json
import webbrowser

API_ENDPOINT = 'https://discord.com/api/v10'
CLIENT_ID = env.CLIENT_ID
CLIENT_SECRET = env.CLIENT_SECRET
REDIRECT_URI = 'http://localhost:3000/auth/login'

app = fastapi.FastAPI()

def get_user_id(token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    r = requests.get('%s/users/@me' % API_ENDPOINT, headers=headers)
    r.raise_for_status()
    return r.json()

@app.get('/auth/login')
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
    return user

def open_login():
    webbrowser.open(f'https://discord.com/oauth2/authorize?client_id=1175725825493045268&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Flogin&scope=identify')

if __name__ == '__main__':
    open_login()
    uvicorn.run(app, host='localhost', port=3000)