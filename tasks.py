import os
import logging
from logging.handlers import RotatingFileHandler
from telegram import Bot
from telegram.error import BadRequest, Forbidden
import asyncio
from dotenv import load_dotenv
from redis import Redis
from rq import Queue
from rq.worker import SimpleWorker

# Configure logging for tasks
LOG_DIR = os.getenv('LOG_DIR', 'logs')
try:
    os.makedirs(LOG_DIR, exist_ok=True)
except Exception:
    pass
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        RotatingFileHandler(os.path.join(LOG_DIR, 'worker.log'), maxBytes=2000000, backupCount=3, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get bot token from environment
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
REDIS_URL = os.getenv('REDIS_URL')
QUEUE_NAME = os.getenv('QUEUE_NAME', 'movie_sending_queue')

def send_video_task(chat_id, video_file_id, caption):
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set in environment variables. Cannot send video.")
        return

    bot = Bot(token=BOT_TOKEN)
    
    try:
        asyncio.run(bot.send_video(chat_id=chat_id, video=video_file_id, caption=caption))
        logger.info(f"Video '{caption}' ({video_file_id}) sent to chat {chat_id} successfully.")
    except (BadRequest, Forbidden) as e:
        logger.error(f"Telegram API xatosi (BadRequest/Forbidden) videoni yuborishda {chat_id} chatiga: {e}")
    except Exception as e:
        logger.error(f"Kutilmagan xatolik videoni yuborishda {chat_id} chatiga: {e}")

if __name__ == "__main__":
    try:
        if REDIS_URL:
            redis_conn = Redis.from_url(REDIS_URL)
        else:
            redis_conn = Redis(host='localhost', port=6379)
        queue = Queue(QUEUE_NAME, connection=redis_conn)
        worker = SimpleWorker([queue], connection=redis_conn)
        logger.info(f"Windows uchun SimpleWorker ishga tushdi. Navbat: {QUEUE_NAME}")
        worker.work(with_scheduler=False)
    except KeyboardInterrupt:
        logger.info("Worker to'xtatildi (KeyboardInterrupt).")
    except Exception as e:
        logger.critical(f"Worker kutilmaganda to'xtadi: {e}", exc_info=True)
