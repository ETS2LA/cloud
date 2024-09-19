ETS2LA Backend server code.

## Installation
add a .env file in the root directory with the following content:
```
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
ENCRYPTION_KEY=your_encryption_key
```
Then run the following commands:
```
pip install -r requirements.txt
python main.py
```

## Explanation
- `CLIENT_ID` and `CLIENT_SECRET` are the credentials for a Discord application.
- `ENCRYPTION_KEY` is a key used to encrypt and decrypt the user's Discord ID and various other sensitive data.