import httpx
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('BOT_TOKEN')

def test_request(url: str, label: str):
    print(f"Testing: {label}")
    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(url)
            print(f"Status Code: {response.status_code}")
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False

test_request("https://www.google.com", "Google")
if token:
    real_url = f"https://api.telegram.org/bot{token}/getMe"
    test_request(real_url, "Telegram getMe (token redacted)")
else:
    print("BOT_TOKEN missing; skip Telegram getMe test")
