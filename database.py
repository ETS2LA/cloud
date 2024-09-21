from cryptography.fernet import Fernet
from env import env
import classes
import hashlib
import json
import time
import os

PATH: str = "data"
EXPIRY: int = 604800 # 1 week
crypt = Fernet(env.ENCRYPTION_KEY.encode())

if not os.path.exists(PATH):
    os.makedirs(PATH)

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
        with open(f"{PATH}/{user_id}/user.json", "r") as f:
            data = json.loads(f.read())
            return decrypt(data["access_token"]) == token
    except Exception:
        return False
    
def update_user_token(user_id: str, token: str) -> DatabaseResponse:
    try:
        with open(f"{PATH}/{user_id}/user.json", "r") as f:
            data = json.loads(f.read())
            data["last_updated"] = time.time()
            data["expiry"] = time.time() + EXPIRY
            data["access_token"] = encrypt(token)
        with open(f"{PATH}/{user_id}/user.json", "w") as f:
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
        if os.path.exists(f"{PATH}/{user_id}/user.json"):
            return DatabaseResponse({"error": "User already exists."}, 400)
        
        os.makedirs(f"{PATH}/{user_id}")
        token = create_user_access_token()
        with open(f"{PATH}/{user_id}/user.json", "w") as f:
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
        with open(f"{PATH}/{user_id}/user.json", "r") as f:
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
        for file in os.listdir(f"{PATH}/{user_id}"):
            os.remove(f"{PATH}/{user_id}/{file}")
        os.rmdir(f"{PATH}/{user_id}")
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
        if not os.path.exists(f"{PATH}/{user_id}/jobs.json"):
            with open(f"{PATH}/{user_id}/jobs.json", "w") as f:
                f.write(json.dumps(
                    {
                        "current_job": job.json(),
                        "completed_jobs": []
                    }, indent=4))
            return DatabaseResponse({"success": "Job started successfully."}, 200)
        
        data = json.loads(open(f"{PATH}/{user_id}/jobs.json", "r").read())
        data["current_job"] = job.json()
        with open(f"{PATH}/{user_id}/jobs.json", "w") as f:
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
        if not os.path.exists(f"{PATH}/{user_id}/jobs.json"):
            return DatabaseResponse({"error": "You can't finish a job that has not been started."}, 400)
        
        data = json.loads(open(f"{PATH}/{user_id}/jobs.json", "r").read())
        
        if data["current_job"] == {}:
            return DatabaseResponse({"error": "You can't finish a job that has not been started."}, 400)

        if not classes.IsFinishedJobSameAsStartedJob(classes.Job(**data["current_job"]), job):
            return DatabaseResponse({"error": "You can't finish a job that is different from the one you started."}, 400)
        
        data["current_job"] = {}
        data["completed_jobs"].append(job.json())
        with open(f"{PATH}/{user_id}/jobs.json", "w") as f:
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
        if not os.path.exists(f"{PATH}/{user_id}/jobs.json"):
            return DatabaseResponse({"error": "You can't cancel a job that has not been started."}, 400)
        
        data = json.loads(open(f"{PATH}/{user_id}/jobs.json", "r").read())
        
        if data["current_job"] == {}:
            return DatabaseResponse({"error": "You can't cancel a job that has not been started."}, 400)
        
        data["current_job"] = {}
        
        with open(f"{PATH}/{user_id}/jobs.json", "w") as f:
            f.write(json.dumps(data, indent=4))
            
        return DatabaseResponse({"success": "Job cancelled successfully."}, 200)
    except FileNotFoundError:
        return DatabaseResponse({"error": "User not found."}, 404)
    except Exception as e:
        return DatabaseResponse({"error": str(e)}, 500)