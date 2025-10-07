from cryptography.fernet import Fernet
from env import env
import classes
import hashlib
import math
import json
import time
import os

PATH: str = "data"
EXPIRY: int = 604800 # 1 week
try:
    crypt = Fernet(env.ENCRYPTION_KEY.encode())
except Exception:
    key = Fernet.generate_key()
    print(f"Didn't find ecnryption key. Generated new key: {key.decode()}")
    input("Please enter that key into the .env file (ENCRYPTION_KEY) and restart the server.")
    exit()

def verify_folder(path) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
        
verify_folder(PATH)
verify_folder(f"{PATH}/users")
verify_folder(f"{PATH}/commits")
verify_folder(f"{PATH}/tracking")

tracking_data = classes.TrackingData()
tracking_data.load_from_pickle(f"{PATH}/tracking.pkl")
tracking_data.update_stats()

# MARK: Auth

def create_user_access_token() -> str:
    return hashlib.sha256(str(time.time()).encode()).hexdigest()

def encrypt(data: str) -> str:
    return crypt.encrypt(data.encode()).decode()

def decrypt(data: str) -> str:
    return crypt.decrypt(data.encode()).decode()

def verify_token(user_id: str, token: str) -> bool:
    try:
        token = token.split(" ")[1]
        with open(f"{PATH}/users/{user_id}/user.json", "r") as f:
            data = json.loads(f.read())
            return decrypt(data["access_token"]) == token
    except Exception:
        return False
    
def update_user_token(user_id: str, token: str) -> classes.Response:
    try:
        with open(f"{PATH}/users/{user_id}/user.json", "r") as f:
            data = json.loads(f.read())
            data["last_updated"] = time.time()
            data["expiry"] = time.time() + EXPIRY
            data["access_token"] = encrypt(token)
        with open(f"{PATH}/users/{user_id}/user.json", "w") as f:
            f.write(json.dumps(data, indent=4))
        return classes.Response({"success": "Token updated successfully."}, 200)
    except FileNotFoundError:
        return classes.Response({"error": "User not found."}, 404)
    except Exception as e:
        return classes.Response({"error": str(e)}, 500)

def get_new_token(user_id: str) -> classes.Response:
    token = create_user_access_token()
    if update_user_token(user_id, token).status != 200:
        return classes.Response({"error": "Failed to update token."}, 500)
    return classes.Response({"success": "New token issued.", "user_id": user_id, "token": token, "expiry": time.time() + EXPIRY}, 200)

def create_user(user_id: str, username: str) -> classes.Response:
    try:
        if os.path.exists(f"{PATH}/users/{user_id}/user.json"):
            return classes.Response({"error": "User already exists."}, 400)
        
        os.makedirs(f"{PATH}/users/{user_id}")
        token = create_user_access_token()
        with open(f"{PATH}/users/{user_id}/user.json", "w") as f:
            f.write(json.dumps({
                "user_id": encrypt(user_id),
                "username": username,
                "created_at": time.time(),
                "last_updated": time.time(),
                "expiry": time.time() + EXPIRY,
                "access_token": encrypt(token)
            }, indent=4))
        return classes.Response({"success": "User created successfully.", "user_id": user_id, "token": token, "expiry": time.time() + EXPIRY}, 200)
    except Exception as e:
        return classes.Response({"error": str(e)}, 500)

# MARK: User

def get_user(user_id: str, token: str) -> classes.Response:
    if not verify_token(user_id, token):
        return classes.Response({"error": "Invalid token."}, 401)
    
    try:
        with open(f"{PATH}/users/{user_id}/user.json", "r") as f:
            data = json.loads(f.read())
            data["user_id"] = decrypt(data["user_id"]) 
            data["access_token"] = decrypt(data["access_token"])   
        
        return classes.Response(data, 200)
    except FileNotFoundError:
        return classes.Response({"error": "User not found."}, 404)
    except Exception as e:
        return classes.Response({"error": str(e)}, 500)
    
def delete_user(user_id: str, token: str) -> classes.Response:
    if not verify_token(user_id, token):
        return classes.Response({"error": "Invalid token."}, 401)
    
    try:
        for file in os.listdir(f"{PATH}/users/{user_id}"):
            os.remove(f"{PATH}/users/{user_id}/{file}")
        os.rmdir(f"{PATH}/users/{user_id}")
        return classes.Response({"success": "User deleted successfully."}, 200)
    except FileNotFoundError:
        return classes.Response({"error": "User not found."}, 404)
    except Exception as e:
        return classes.Response({"error": str(e)}, 500)
    
# MARK: Jobs

def job_started(user_id:str, token:str, job: classes.Job) -> classes.Response:
    if not verify_token(user_id, token):
        return classes.Response({"error": "Invalid token."}, 401)
    
    try:
        if not os.path.exists(f"{PATH}/users/{user_id}/jobs.json"):
            with open(f"{PATH}/users/{user_id}/jobs.json", "w") as f:
                f.write(json.dumps(
                    {
                        "current_job": job.json(),
                        "completed_jobs": []
                    }, indent=4))
            return classes.Response({"success": "Job started successfully."}, 200)
        
        data = json.loads(open(f"{PATH}/users/{user_id}/jobs.json", "r").read())
        data["current_job"] = job.json()
        with open(f"{PATH}/users/{user_id}/jobs.json", "w") as f:
            f.write(json.dumps(data, indent=4))
            
        return classes.Response({"success": "Job started successfully."}, 200)
        
    except FileNotFoundError:
        return classes.Response({"error": "User not found."}, 404)
    except Exception as e:
        return classes.Response({"error": str(e)}, 500)
    
def job_finished(user_id:str, token:str, job: classes.FinishedJob) -> classes.Response:
    if not verify_token(user_id, token):
        return classes.Response({"error": "Invalid token."}, 401)
    
    try:
        if not os.path.exists(f"{PATH}/users/{user_id}/jobs.json"):
            return classes.Response({"error": "You can't finish a job that has not been started."}, 400)
        
        data = json.loads(open(f"{PATH}/users/{user_id}/jobs.json", "r").read())
        
        if data["current_job"] == {}:
            return classes.Response({"error": "You can't finish a job that has not been started."}, 400)

        if not classes.IsFinishedJobSameAsStartedJob(classes.Job(**data["current_job"]), job):
            return classes.Response({"error": "You can't finish a job that is different from the one you started."}, 400)
        
        data["current_job"] = {}
        data["completed_jobs"].append(job.json())
        with open(f"{PATH}/users/{user_id}/jobs.json", "w") as f:
            f.write(json.dumps(data, indent=4))
            
        return classes.Response({"success": "Job finished successfully."}, 200)
    except FileNotFoundError:
        return classes.Response({"error": "User not found."}, 404)
    except Exception as e:
        return classes.Response({"error": str(e)}, 500)
    
def job_cancelled(user_id:str, token:str, job: classes.CancelledJob) -> classes.Response:
    if not verify_token(user_id, token):
        return classes.Response({"error": "Invalid token."}, 401)
    
    try:
        if not os.path.exists(f"{PATH}/users/{user_id}/jobs.json"):
            return classes.Response({"error": "You can't cancel a job that has not been started."}, 400)
        
        data = json.loads(open(f"{PATH}/users/{user_id}/jobs.json", "r").read())
        
        if data["current_job"] == {}:
            return classes.Response({"error": "You can't cancel a job that has not been started."}, 400)
        
        data["current_job"] = {}
        
        with open(f"{PATH}/users/{user_id}/jobs.json", "w") as f:
            f.write(json.dumps(data, indent=4))
            
        return classes.Response({"success": "Job cancelled successfully."}, 200)
    except FileNotFoundError:
        return classes.Response({"error": "User not found."}, 404)
    except Exception as e:
        return classes.Response({"error": str(e)}, 500)
    
def get_jobs(user_id: str, token: str) -> classes.Response:
    if not verify_token(user_id, token):
        return classes.Response({"error": "Invalid token."}, 401)
    
    try:
        if not os.path.exists(f"{PATH}/users/{user_id}/jobs.json"):
            return classes.Response({"error": "No jobs found."}, 404)
        
        data = json.loads(open(f"{PATH}/users/{user_id}/jobs.json", "r").read())
        data = data["completed_jobs"]
        return classes.Response(data, 200)
    except FileNotFoundError:
        return classes.Response({"error": "User not found."}, 404)
    except Exception as e:
        return classes.Response({"error": str(e)}, 500)
    
# MARK: Commits

def verify_commit_file(commit_id: str) -> bool:
    try:
        if not os.path.exists(f"{PATH}/commits/{commit_id}.json"):    
            try:
                with open(f"{PATH}/commits/{commit_id}.json", "w") as f:
                    f.write(json.dumps({
                        "updated_users": [],
                        "emotes": []
                    }, indent=4))
                return True
            except Exception:
                return False
        return True
    except Exception:
        return False

def get_commit_info(commit_id: str) -> classes.Response:
    try:
        if not os.path.exists(f"{PATH}/commits/{commit_id}.json"):
            return classes.Response({"error": "Commit not found."}, 404)
        
        data = json.loads(open(f"{PATH}/commits/{commit_id}.json", "r").read())
        return classes.Response(data, 200)
    except FileNotFoundError:
        return classes.Response({"error": "Commit not found."}, 404)
    except Exception as e:
        return classes.Response({"error": str(e)}, 500)

def mark_commit_updated(user_id: str, token: str, commits: classes.UpdatedCommits):
    if not verify_token(user_id, token):
        return classes.Response({"error": "Invalid token."}, 401)
    
    try:
        for commit in commits.commits:
            if not os.path.exists(f"{PATH}/commits/{commit}.json"):
                return classes.Response({"error": "Commit not found."}, 404)
            else:
                data = json.loads(open(f"{PATH}/commits/{commit}.json", "r").read())
                data["updated_users"].append(user_id)
                with open(f"{PATH}/commits/{commit}.json", "w") as f:
                    f.write(json.dumps(data, indent=4))
                    
        return classes.Response({"success": "Commits updated successfully."}, 200)
    except FileNotFoundError:
        return classes.Response({"error": "User not found."}, 404)
    except Exception as e:
        return classes.Response({"error": str(e)}, 500)
    
def add_emote_to_commit(user_id: str, token: str, commit_id: str, emote: str) -> classes.Response:
    if not verify_token(user_id, token):
        return classes.Response({"error": "Invalid token."}, 401)
    
    if not verify_commit_file(commit_id):
        return classes.Response({"error": "Commit not found."}, 404)
    
    try:
        data = json.loads(open(f"{PATH}/commits/{commit_id}.json", "r").read())
        data["emotes"].append({
            "user_id": user_id,
            "emote": emote
        })
        with open(f"{PATH}/commits/{commit_id}.json", "w") as f:
            f.write(json.dumps(data, indent=4))
            
        return classes.Response({"success": "Emote added to commit successfully."}, 200)
    except FileNotFoundError:
        return classes.Response({"error": "Commit not found."}, 404)
    except Exception as e:
        return classes.Response({"error": str(e)}, 500)
    
def remove_emote_from_commit(user_id: str, token: str, commit_id: str, emote: str) -> classes.Response:
    if not verify_token(user_id, token):
        return classes.Response({"error": "Invalid token."}, 401)
    
    if not verify_commit_file(commit_id):
        return classes.Response({"error": "Commit not found."}, 404)
    
    try:
        data = json.loads(open(f"{PATH}/commits/{commit_id}.json", "r").read())
        for i, e in enumerate(data["emotes"]):
            if e["user_id"] == user_id and e["emote"] == emote:
                data["emotes"].pop(i)
                with open(f"{PATH}/commits/{commit_id}.json", "w") as f:
                    f.write(json.dumps(data, indent=4))
                return classes.Response({"success": "Emote removed from commit successfully."}, 200)
            
        return classes.Response({"error": "Emote not found in commit."}, 404)
    except FileNotFoundError:
        return classes.Response({"error": "Commit not found."}, 404)
    except Exception as e:
        return classes.Response({"error": str(e)}, 500)
    
# MARK: Tracking

def verify_user_folder(user_id: str):
    if user_id not in tracking_data.users:
        tracking_data.users[user_id] = classes.UserSessionData()

def ping(user_id: str) -> classes.Response:
    verify_user_folder(user_id)
    
    data = tracking_data.users[user_id]
    data.latest = time.time()
    
    if len(data.sessions) == 0:
        data.sessions.append(classes.SessionData(data.latest, data.latest))
    elif data.latest - data.sessions[-1].end > 180: # 3 minutes
        data.sessions.append(classes.SessionData(data.latest, data.latest))
    else:
        data.sessions[-1].end = data.latest

    data.total = sum(s.end - s.start for s in data.sessions)
    tracking_data.save_to_pickle(f"{PATH}/tracking.pkl")
    return classes.Response({"success": "Ping recorded."}, 200)

def get_time_used(user_id: str) -> classes.Response:
    verify_user_folder(user_id)
    try:
        data = tracking_data.users[user_id]
        time_used = data.total    
        return classes.Response({
            "time_used": time_used,
            "sessions": len(data.sessions)
        }, 200)
    except FileNotFoundError:
        return classes.Response({"error": "No pings found."}, 404)

def get_unique_user_counts() -> classes.Response:
    tracking_data.update_stats()
    dictionary = {
        "1h": tracking_data.last_1h,
        "1d": tracking_data.last_1d,
        "7d": tracking_data.last_7d,
        "30d": tracking_data.last_30d,
        "total_users": len(tracking_data.users),
        "total_tracked_hours": sum(u.total for u in tracking_data.users.values()) / 3600
    }
    return classes.Response(dictionary, 200)
    
def get_online_user_count() -> classes.Response:
    tracking_data.update_current_users()
    unique_users = get_unique_user_counts().data
    return classes.Response({"online": tracking_data.last_180s, "unique": unique_users}, 200)