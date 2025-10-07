from env import env
import requests
import classes
import time
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

users = ["304923494570000384"]
def test_ping():
    for user in users:
        r = requests.get(f'http://localhost:8000/tracking/ping/{user}')
        print(r.json())

def test_get_time():
    for user in users:
        r = requests.get(f'http://localhost:8000/tracking/time/{user}')
        print(r.json())
        
def test_get_sessions():
    for user in users:
        r = requests.get(f'http://localhost:8000/tracking/sessions/{user}')
        print(r.json())
        
def test_get_online_users():
    r = requests.get('http://localhost:8000/tracking/users')
    print(r.json())

def test_crash_report():
    data = {
        "timestamp": 1234567890,
        "source": "test_source",
        "source_description": "This is a test crash report",
        "fields": {
            "field1": "value1",
            "field2": "value2"
        }
    }
    r = requests.post('http://localhost:8000/crash/report', json=data)
    print(r.json())

def test_feedback():
    data = {
        "timestamp": int(time.time()),
        "message": "Tämä viesti on suomeksi.",
        "user": "test_user",
        "fields": {}
    }
    r = requests.post('http://localhost:8000/feedback', json=data)
    print(r.json())
    
def test_kofi():
    data = "data=%7b%22verification_token%22%3a%221f7f09ae-fe10-4b49-99c5-6a3761e70d04%22%2c%22message_id%22%3a%221926302d-004d-492f-9e59-8d68811d153c%22%2c%22timestamp%22%3a%222025-09-02T13%3a26%3a06Z%22%2c%22type%22%3a%22Donation%22%2c%22is_public%22%3atrue%2c%22from_name%22%3a%22Jo+Example%22%2c%22message%22%3a%22Good+luck+with+the+integration!%22%2c%22amount%22%3a%223.00%22%2c%22url%22%3a%22https%3a%2f%2fko-fi.com%2fHome%2fCoffeeShop%3ftxid%3d00000000-1111-2222-3333-444444444444%22%2c%22email%22%3a%22jo.example%40example.com%22%2c%22currency%22%3a%22USD%22%2c%22is_subscription_payment%22%3afalse%2c%22is_first_subscription_payment%22%3afalse%2c%22kofi_transaction_id%22%3a%2200000000-1111-2222-3333-444444444444%22%2c%22shop_items%22%3anull%2c%22tier_name%22%3anull%2c%22shipping%22%3anull%2c%22discord_username%22%3a%22Jo%234105%22%2c%22discord_userid%22%3a%22012345678901234567%22%7d"
    r = requests.post('http://localhost:8000/kofi', data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    print(r.json())

# print(test_delete_user())
# 
# print(test_get_user())
# 
# # Test cancel job
# print(test_start_job())
# print(test_cancel_job())
# 
# # Test finish job without starting
# print(test_finish_job())
# 
# # Test start and finish job
# print(test_start_job())
# print(test_finish_job())
# 
# # Test cancel job without starting / after finishing
# print(test_cancel_job())    
# 
# # Test start and finish job
# print(test_start_job())
# print(test_finish_job())
# 
# # Test start job
# print(test_start_job())

# END RESULT:
# jobs.json:
# current_job: a job
# completed_jobs: two finished jobs

# import time
# while True:
#     print("\n\n\n\n\n-- Pinging --")
#     test_ping()
#     print("-- Getting time --")
#     test_get_time()
#     print("-- Getting online users --")
#     test_get_online_users()
#     time.sleep(5)

#test_crash_report()
#test_feedback()

# test_kofi()

test_get_sessions()