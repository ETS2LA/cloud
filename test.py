import requests

def test_get_user(user_id, token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    r = requests.get(f'http://localhost:8000/user/{user_id}', headers=headers)
    return r.json()