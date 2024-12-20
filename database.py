from cryptography.fernet import Fernet
from typing import List
from env import env
import classes
import hashlib
import json
import time
import os

PATH: str = "data"
EXPIRY: int = 604800 # 1 week
crypt = Fernet(env.ENCRYPTION_KEY.encode())

def verify_folders() -> None:
    if not os.path.exists(PATH):
        os.makedirs(PATH)

    if not os.path.exists(f"{PATH}/users"):
        os.makedirs(f"{PATH}/users", exist_ok=True)
        
    if not os.path.exists(f"{PATH}/commits"):
        os.makedirs(f"{PATH}/commits", exist_ok=True)
        
verify_folders()

class DatabaseResponse:
    def __init__(self, data: dict, status: int) -> None:
        self.data = data
        self.status = status

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
    
def update_user_token(user_id: str, token: str) -> DatabaseResponse:
    try:
        with open(f"{PATH}/users/{user_id}/user.json", "r") as f:
            data = json.loads(f.read())
            data["last_updated"] = time.time()
            data["expiry"] = time.time() + EXPIRY
            data["access_token"] = encrypt(token)
        with open(f"{PATH}/users/{user_id}/user.json", "w") as f:
            f.write(json.dumps(data, indent=4))
        return DatabaseResponse({"success": "Token updated successfully."}, 200)
    except FileNotFoundError:
        return DatabaseResponse({"error": "User not found."}, 404)
    except Exception as e:
        return DatabaseResponse({"error": str(e)}, 500)

def get_new_token(user_id: str) -> DatabaseResponse:
    token = create_user_access_token()
    if update_user_token(user_id, token).status != 200:
        return DatabaseResponse({"error": "Failed to update token."}, 500)
    return DatabaseResponse({"success": "New token issued.", "user_id": user_id, "token": token, "expiry": time.time() + EXPIRY}, 200)

def create_user(user_id: str, username: str) -> DatabaseResponse:
    try:
        if os.path.exists(f"{PATH}/users/{user_id}/user.json"):
            return DatabaseResponse({"error": "User already exists."}, 400)
        
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
        return DatabaseResponse({"success": "User created successfully.", "user_id": user_id, "token": token, "expiry": time.time() + EXPIRY}, 200)
    except Exception as e:
        return DatabaseResponse({"error": str(e)}, 500)

# MARK: User

def get_user(user_id: str, token: str) -> DatabaseResponse:
    if not verify_token(user_id, token):
        return DatabaseResponse({"error": "Invalid token."}, 401)
    
    try:
        with open(f"{PATH}/users/{user_id}/user.json", "r") as f:
            data = json.loads(f.read())
            data["user_id"] = decrypt(data["user_id"]) 
            data["access_token"] = decrypt(data["access_token"])   
        
        return DatabaseResponse(data, 200)
    except FileNotFoundError:
        return DatabaseResponse({"error": "User not found."}, 404)
    except Exception as e:
        return DatabaseResponse({"error": str(e)}, 500)
    
def delete_user(user_id: str, token: str) -> DatabaseResponse:
    if not verify_token(user_id, token):
        return DatabaseResponse({"error": "Invalid token."}, 401)
    
    try:
        for file in os.listdir(f"{PATH}/users/{user_id}"):
            os.remove(f"{PATH}/users/{user_id}/{file}")
        os.rmdir(f"{PATH}/users/{user_id}")
        return DatabaseResponse({"success": "User deleted successfully."}, 200)
    except FileNotFoundError:
        return DatabaseResponse({"error": "User not found."}, 404)
    except Exception as e:
        return DatabaseResponse({"error": str(e)}, 500)
    
# MARK: Jobs

def job_started(user_id:str, token:str, job: classes.Job) -> DatabaseResponse:
    if not verify_token(user_id, token):
        return DatabaseResponse({"error": "Invalid token."}, 401)
    
    try:
        if not os.path.exists(f"{PATH}/users/{user_id}/jobs.json"):
            with open(f"{PATH}/users/{user_id}/jobs.json", "w") as f:
                f.write(json.dumps(
                    {
                        "current_job": job.json(),
                        "completed_jobs": []
                    }, indent=4))
            return DatabaseResponse({"success": "Job started successfully."}, 200)
        
        data = json.loads(open(f"{PATH}/users/{user_id}/jobs.json", "r").read())
        data["current_job"] = job.json()
        with open(f"{PATH}/users/{user_id}/jobs.json", "w") as f:
            f.write(json.dumps(data, indent=4))
            
        return DatabaseResponse({"success": "Job started successfully."}, 200)
        
    except FileNotFoundError:
        return DatabaseResponse({"error": "User not found."}, 404)
    except Exception as e:
        return DatabaseResponse({"error": str(e)}, 500)
    
def job_finished(user_id:str, token:str, job: classes.FinishedJob) -> DatabaseResponse:
    if not verify_token(user_id, token):
        return DatabaseResponse({"error": "Invalid token."}, 401)
    
    try:
        if not os.path.exists(f"{PATH}/users/{user_id}/jobs.json"):
            return DatabaseResponse({"error": "You can't finish a job that has not been started."}, 400)
        
        data = json.loads(open(f"{PATH}/users/{user_id}/jobs.json", "r").read())
        
        if data["current_job"] == {}:
            return DatabaseResponse({"error": "You can't finish a job that has not been started."}, 400)

        if not classes.IsFinishedJobSameAsStartedJob(classes.Job(**data["current_job"]), job):
            return DatabaseResponse({"error": "You can't finish a job that is different from the one you started."}, 400)
        
        data["current_job"] = {}
        data["completed_jobs"].append(job.json())
        with open(f"{PATH}/users/{user_id}/jobs.json", "w") as f:
            f.write(json.dumps(data, indent=4))
            
        return DatabaseResponse({"success": "Job finished successfully."}, 200)
    except FileNotFoundError:
        return DatabaseResponse({"error": "User not found."}, 404)
    except Exception as e:
        return DatabaseResponse({"error": str(e)}, 500)
    
def job_cancelled(user_id:str, token:str, job: classes.CancelledJob) -> DatabaseResponse:
    if not verify_token(user_id, token):
        return DatabaseResponse({"error": "Invalid token."}, 401)
    
    try:
        if not os.path.exists(f"{PATH}/users/{user_id}/jobs.json"):
            return DatabaseResponse({"error": "You can't cancel a job that has not been started."}, 400)
        
        data = json.loads(open(f"{PATH}/users/{user_id}/jobs.json", "r").read())
        
        if data["current_job"] == {}:
            return DatabaseResponse({"error": "You can't cancel a job that has not been started."}, 400)
        
        data["current_job"] = {}
        
        with open(f"{PATH}/users/{user_id}/jobs.json", "w") as f:
            f.write(json.dumps(data, indent=4))
            
        return DatabaseResponse({"success": "Job cancelled successfully."}, 200)
    except FileNotFoundError:
        return DatabaseResponse({"error": "User not found."}, 404)
    except Exception as e:
        return DatabaseResponse({"error": str(e)}, 500)
    
def get_jobs(user_id: str, token: str) -> DatabaseResponse:
    if not verify_token(user_id, token):
        return DatabaseResponse({"error": "Invalid token."}, 401)
    
    try:
        if not os.path.exists(f"{PATH}/users/{user_id}/jobs.json"):
            return DatabaseResponse({"error": "No jobs found."}, 404)
        
        data = json.loads(open(f"{PATH}/users/{user_id}/jobs.json", "r").read())
        data = data["completed_jobs"]
        return DatabaseResponse(data, 200)
    except FileNotFoundError:
        return DatabaseResponse({"error": "User not found."}, 404)
    except Exception as e:
        return DatabaseResponse({"error": str(e)}, 500)
    
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

def get_commit_info(commit_id: str) -> DatabaseResponse:
    try:
        if not os.path.exists(f"{PATH}/commits/{commit_id}.json"):
            return DatabaseResponse({"error": "Commit not found."}, 404)
        
        data = json.loads(open(f"{PATH}/commits/{commit_id}.json", "r").read())
        return DatabaseResponse(data, 200)
    except FileNotFoundError:
        return DatabaseResponse({"error": "Commit not found."}, 404)
    except Exception as e:
        return DatabaseResponse({"error": str(e)}, 500)

def mark_commit_updated(user_id: str, token: str, commits: classes.UpdatedCommits):
    if not verify_token(user_id, token):
        return DatabaseResponse({"error": "Invalid token."}, 401)
    
    try:
        for commit in commits.commits:
            if not os.path.exists(f"{PATH}/commits/{commit}.json"):
                return DatabaseResponse({"error": "Commit not found."}, 404)
            else:
                data = json.loads(open(f"{PATH}/commits/{commit}.json", "r").read())
                data["updated_users"].append(user_id)
                with open(f"{PATH}/commits/{commit}.json", "w") as f:
                    f.write(json.dumps(data, indent=4))
                    
        return DatabaseResponse({"success": "Commits updated successfully."}, 200)
    except FileNotFoundError:
        return DatabaseResponse({"error": "User not found."}, 404)
    except Exception as e:
        return DatabaseResponse({"error": str(e)}, 500)
    
def add_emote_to_commit(user_id: str, token: str, commit_id: str, emote: str) -> DatabaseResponse:
    if not verify_token(user_id, token):
        return DatabaseResponse({"error": "Invalid token."}, 401)
    
    if not verify_commit_file(commit_id):
        return DatabaseResponse({"error": "Commit not found."}, 404)
    
    try:
        data = json.loads(open(f"{PATH}/commits/{commit_id}.json", "r").read())
        data["emotes"].append({
            "user_id": user_id,
            "emote": emote
        })
        with open(f"{PATH}/commits/{commit_id}.json", "w") as f:
            f.write(json.dumps(data, indent=4))
            
        return DatabaseResponse({"success": "Emote added to commit successfully."}, 200)
    except FileNotFoundError:
        return DatabaseResponse({"error": "Commit not found."}, 404)
    except Exception as e:
        return DatabaseResponse({"error": str(e)}, 500)
    
def remove_emote_from_commit(user_id: str, token: str, commit_id: str, emote: str) -> DatabaseResponse:
    if not verify_token(user_id, token):
        return DatabaseResponse({"error": "Invalid token."}, 401)
    
    if not verify_commit_file(commit_id):
        return DatabaseResponse({"error": "Commit not found."}, 404)
    
    try:
        data = json.loads(open(f"{PATH}/commits/{commit_id}.json", "r").read())
        for i, e in enumerate(data["emotes"]):
            if e["user_id"] == user_id and e["emote"] == emote:
                data["emotes"].pop(i)
                with open(f"{PATH}/commits/{commit_id}.json", "w") as f:
                    f.write(json.dumps(data, indent=4))
                return DatabaseResponse({"success": "Emote removed from commit successfully."}, 200)
            
        return DatabaseResponse({"error": "Emote not found in commit."}, 404)
    except FileNotFoundError:
        return DatabaseResponse({"error": "Commit not found."}, 404)
    except Exception as e:
        return DatabaseResponse({"error": str(e)}, 500)