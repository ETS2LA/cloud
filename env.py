"""
Create a .env file with the following keys:
CLIENT_ID=your_discord_client_id
CLIENT_SECRET=your_discord_client_secret
ENCRYPTION_KEY=enctyption_key_for_tokens
CRASH_WEBHOOK=discord_webhook_url_for_crash_reports
FEEDBACK_WEBHOOK=discord_webhook_url_for_feedback
"""

from types import SimpleNamespace

envData = open(".env", "r").readlines()
envData = [x.strip() for x in envData]

dictionary = {}
for i in envData:
    dictionary[i.split("=")[0]] = i.replace(i.split("=")[0] + "=", "") # support for multiple = in value

env = SimpleNamespace(**dictionary)