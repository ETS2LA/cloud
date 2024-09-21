from env import env
import requests
import classes
import json

user_id = env.TEST_USER_ID
token = env.TEST_USER_TOKEN

def test_get_user():
    headers = {
        'Authorization': f'Bearer {token}'
    }
    r = requests.get(f'http://localhost:8000/user/{user_id}', headers=headers)
    return r.json()

def test_delete_user():
    headers = {
        'Authorization': f'Bearer {token}'
    }
    r = requests.get(f'http://localhost:8000/delete/{user_id}', headers=headers)
    return r.json()

def test_start_job():
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = classes.Job().json()
    r = requests.post(f'http://localhost:8000/user/{user_id}/job/started', headers=headers, json=data)
    return r.json()

def test_cancel_job():
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = classes.CancelledJob().json()
    r = requests.post(f'http://localhost:8000/user/{user_id}/job/cancelled', headers=headers, json=data)
    return r.json()

def test_finish_job():
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = classes.FinishedJob().json()
    r = requests.post(f'http://localhost:8000/user/{user_id}/job/finished', headers=headers, json=data)
    return r.json()

print(test_delete_user())

print(test_get_user())

# Test cancel job
print(test_start_job())
print(test_cancel_job())

# Test finish job without starting
print(test_finish_job())

# Test start and finish job
print(test_start_job())
print(test_finish_job())

# Test cancel job without starting / after finishing
print(test_cancel_job())    

# Test start and finish job
print(test_start_job())
print(test_finish_job())

# Test start job
print(test_start_job())

# END RESULT:
# jobs.json:
# current_job: a job
# completed_jobs: two finished jobs