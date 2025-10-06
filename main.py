from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from googletrans import Translator
from fastapi import Header
from fastapi import Form
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

# MARK: Tracking

@app.get("/tracking/ping/{user_id}")
def ping(user_id: str):
    return database.ping(user_id)

@app.get("/tracking/time/{user_id}")
def get_user_time(user_id: str):
    return database.get_time_used(user_id)

@app.get("/tracking/users")
def get_online_users():
    return database.get_online_user_count()

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

# MARK: Commits

@app.get('/commits/{commit_id}')
def get_commit_info(commit_id: str):
    return database.get_commit_info(commit_id)

@app.post('/commits/{commit_id}/updated')
def mark_commit_updated(user_id: str, commits: classes.UpdatedCommits, authorization: str = Header(None)):
    if not authorization:
        return {'error': 'No authorization header.'}
    return database.mark_commit_updated(user_id, authorization, commits)

@app.post('/commits/{commit_id}/emote/add')
def add_emote_to_commit(user_id: str, commit_id: str, emote: str, authorization: str = Header(None)):
    if not authorization:
        return {'error': 'No authorization header.'}
    return database.add_emote_to_commit(user_id, authorization, commit_id, emote)

@app.post('/commits/{commit_id}/emote/remove')
def remove_emote_from_commit(user_id: str, commit_id: str, emote: str, authorization: str = Header(None)):
    if not authorization:
        return {'error': 'No authorization header.'}
    return database.remove_emote_from_commit(user_id, authorization, commit_id, emote)

# MARK: Discord Integration

@app.post('/feedback')
async def feedback(feedback: classes.Feedback):
    if not env.FEEDBACK_WEBHOOK:
        return classes.Response({'error': 'No feedback webhook configured.'}, status=500)
    
    data = {
        "embeds": [
            {
                "title": feedback.user,
                "description": feedback.message,
                "color": 5700441,
                "author": {
                    "name": "Feedback"
                },
                "fields": [
                    {"name": k, "value": v, "inline": False} for k, v in feedback.fields.items()
                ],
                "timestamp": str(datetime.fromtimestamp(feedback.timestamp, tz=timezone.utc).isoformat()).split("+")[0] + ".000Z"
            }
        ],
        "content": ""
    }
    
    translation = None
    async with Translator() as translator:
        language = await translator.detect(feedback.message)
        if language.lang != 'en':
            translation = await translator.translate(feedback.message, dest='en')
    
    if translation:
        data['embeds'][0]['fields'].append({"name": f"Translation (from {translation.src})", "value": translation.text, "inline": False})
    
    r = requests.post(env.FEEDBACK_WEBHOOK, json=data)
    if r.status_code != 204:
        return classes.Response({'error': 'Failed to send feedback.', 'stacktrace': r.text}, status=500)
    return classes.Response({'status': 'ok'}, status=200)

@app.post('/crash/report')
def crash_report(report: classes.CrashReport):
    if not env.CRASH_WEBHOOK:
        return classes.Response({'error': 'No crash webhook configured.'}, status=500)
    
    data = {
        "embeds": [
            {
                "title": report.source,
                "description": report.source_description,
                "color": 16471638,
                "author": {
                    "name": "Crash Report"
                },
                "fields": [
                    {"name": k, "value": v, "inline": False} for k, v in report.fields.items()
                ],
                "timestamp": str(datetime.fromtimestamp(report.timestamp, tz=timezone.utc).isoformat()).split("+")[0] + ".000Z"
            }
        ],
        "content": ""
    }
    r = requests.post(env.CRASH_WEBHOOK, json=data)
    if r.status_code != 204:
        return classes.Response({'error': 'Failed to send crash report.', 'stacktrace': r.text}, status=500)
    return classes.Response({'status': 'ok'}, status=200)

@app.post('/kofi')
async def kofi(data: str = Form(...)):
    try:
        parsed_data = json.loads(data)
        
        verification_token = parsed_data.get("verification_token")
        kofi_type = parsed_data.get("type")
        is_public = parsed_data.get("is_public")
        from_name = parsed_data.get("from_name")
        message = parsed_data.get("message")
        discord_username = parsed_data.get("discord_username")
        discord_userid = parsed_data.get("discord_userid")
    except json.JSONDecodeError:
        return classes.Response({'error': 'Invalid JSON in form data.'}, status=400)

    if not env.KOFI_WEBHOOK or not env.KOFI_SECRET:
        return classes.Response({'error': 'Webhook or secret not configured.'}, status=500)

    if verification_token != env.KOFI_SECRET:
        return classes.Response({'error': 'Invalid verification token.'}, status=403)

    name = "Anonymous"
    default_message = "No message provided."
    if is_public:
        name = discord_username if discord_username else from_name
        message = message if message else default_message
    else: 
        message = default_message

    output = {
        "embeds": [
            {
                "title": name,
                "description": f"> {message}",
                "color": 16711680,
                "author": {
                    "name": f"New Ko-Fi {kofi_type}!",
                    "icon_url": "https://cdn.prod.website-files.com/5c14e387dab576fe667689cf/670f5a01229bf8a18f97a3c1_favion.png"
                },
                "fields": []
            }
        ],
        "content": ""
    }

    if discord_userid and is_public:
        output['embeds'][0]['fields'].append({"name": "Discord", "value": f"<@{discord_userid}>", "inline": False})

        time = get_user_time(discord_userid)
        if time.status == 200:
            time_text = ""
            if time.data['time_used'] >= 3600:
                time_text += f"{round(time.data['time_used'] / 3600)} hours"
            if time.data['time_used'] >= 60:
                if time_text:
                    time_text += " and "
                time_text += f"{round((time.data['time_used'] % 3600) / 60)} minutes"

            output['embeds'][0]['fields'].append({"name": "ETS2LA User", "value": time_text, "inline": False})

    output['embeds'][0]['fields'].append({"name": "", "value": "[Ko-Fi](https://ko-fi.com/Tumppi066)", "inline": False})

    r = requests.post(env.KOFI_WEBHOOK, json=output)
    if r.status_code != 204:
        return classes.Response({'error': 'Failed to send Ko-fi notification.', 'stacktrace': r.text}, status=500)
    return classes.Response({'status': 'ok'}, status=200)
    
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