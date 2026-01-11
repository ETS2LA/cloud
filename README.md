> [!NOTE]  
> Along with the ETS2LA C# rewrite this backend will be rewritten. The code quality is _fine_ but there's still a lot of improvement to do. We thought a full rewrite to add new features would work better than trying to wrestle the current version to a state we're happy with.

ETS2LA Backend server code.

## Installation
add a .env file in the root directory with the following content:
```
CLIENT_ID=your_discord_client_id
CLIENT_SECRET=your_discord_client_secret
ENCRYPTION_KEY=enctyption_key_for_tokens
CRASH_WEBHOOK=discord_webhook_url_for_crash_reports
FEEDBACK_WEBHOOK=discord_webhook_url_for_feedback
KOFI_WEBHOOK=discord_webhook_url_for_kofi_notifications
KOFI_SECRET=kofi_secret_for_donations
```
Then run the following commands:
```
pip install -r requirements.txt
python main.py
```
Alternatively use docker:
```
docker compose up
```

## Explanation
- `CLIENT_ID` and `CLIENT_SECRET` are the credentials for a Discord application.
- `ENCRYPTION_KEY` is a key used to encrypt and decrypt the user's Discord ID and various other sensitive data.
- `CRASH_WEBHOOK`, `FEEDBACK_WEBHOOK` and `KOFI_WEBHOOK` are for Discord notifications.
- `KOFI_SECRET` is to ensure we're receiving the correct Kofi user's notifications.

Note that the webhooks are optional, you don't have to assign a value to them (ensure they are present in the file though).
