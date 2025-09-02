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

users = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
def test_ping():
    for user in users:
        r = requests.get(f'http://localhost:8000/tracking/ping/{user}')
        print(r.json())

def test_get_time():
    for user in users:
        r = requests.get(f'http://localhost:8000/tracking/time/{user}')
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
    data = {
        "verification_token": "1f7f09ae-fe10-4b49-99c5-6a3761e70d04",
        "message_id": "bc927216-8409-4046-a496-7447ea208173",
        "timestamp": "2025-09-02T12:35:29Z",
        "type": "Donation",
        "is_public": False,
        "from_name": "Tuomas",
        "message": "Good luck with the integration!",
        "amount": "3.00",
        "url": "https://ko-fi.com/Home/CoffeeShop?txid=00000000-1111-2222-3333-444444444444",
        "email": "jo.example@example.com",
        "currency": "USD",
        "is_subscription_payment": False,
        "is_first_subscription_payment": False,
        "kofi_transaction_id": "00000000-1111-2222-3333-444444444444",
        "shop_items": None,
        "tier_name": None,
        "shipping": None,
        "discord_username": "Tumppi066",
        "discord_userid": "304923494570000384"
    }
    r = requests.post('http://localhost:8000/kofi', json=data)
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

test_kofi()