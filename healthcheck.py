import os
import sys
from dotenv import load_dotenv

def _check_bot() -> int:
    try:
        import httpx
        # Check local Flask server first
        port = os.getenv("PORT", "8080")
        with httpx.Client(timeout=2) as client:
            r = client.get(f"http://localhost:{port}/health")
            if r.status_code != 200:
                return 1
        
        # Then check Telegram API
        load_dotenv()
        token = os.getenv('BOT_TOKEN')
        if not token:
            return 1
        url = f"https://api.telegram.org/bot{token}/getMe"
        with httpx.Client(timeout=5) as client:
            r = client.get(url)
            return 0 if 200 <= r.status_code < 400 else 1
    except Exception:
        return 1

def _check_worker() -> int:
    try:
        from redis import Redis
        load_dotenv()
        url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        conn = Redis.from_url(url)
        pong = conn.ping()
        return 0 if pong else 1
    except Exception:
        return 1

def main():
    role = sys.argv[1] if len(sys.argv) > 1 else 'bot'
    if role == 'bot':
        sys.exit(_check_bot())
    if role == 'worker':
        sys.exit(_check_worker())
    sys.exit(1)

if __name__ == '__main__':
    main()
