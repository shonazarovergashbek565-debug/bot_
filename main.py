import os
import json
import logging
from logging.handlers import RotatingFileHandler
import time
import itertools
import difflib
import telebot
from telebot import types
from dotenv import load_dotenv
from rq import Queue
from redis import Redis
import httpx
from flask import Flask
import threading
from tasks import send_video_task
import database

load_dotenv()

LOG_DIR = os.getenv('LOG_DIR', 'logs')
try:
    os.makedirs(LOG_DIR, exist_ok=True)
except Exception:
    pass
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        RotatingFileHandler(os.path.join(LOG_DIR, 'bot.log'), maxBytes=2000000, backupCount=3, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(i.strip()) for i in os.getenv('ADMIN_IDS', '').split(',') if i.strip()]
logger.info(f"Yuklangan ADMIN_IDS: {ADMIN_IDS}")

# Dastlabki kanallarni bazaga yuklash (agar baza bo'sh bo'lsa)
def init_settings_from_env():
    channels, urls = database.get_channels()
    if not channels:
        env_channels = os.getenv('REQUIRED_CHANNELS', '').split(',')
        env_urls = os.getenv('REQUIRED_CHANNEL_URLS', '').split(',')
        for c, u in zip(env_channels, env_urls):
            if c.strip() and u.strip():
                database.add_channel(c.strip(), u.strip())

database.init_db()
init_settings_from_env()

# Majburiy obuna kanallari
REQUIRED_CHANNELS = [i.strip() for i in os.getenv('REQUIRED_CHANNELS', '-1002643118573').split(',') if i.strip()]
REQUIRED_CHANNEL_URLS = [i.strip() for i in os.getenv('REQUIRED_CHANNEL_URLS', 'https://t.me/+UkWjlZ2-SFoyZDBi').split(',') if i.strip()]

CDN_BASE_URLS = [u.strip() for u in os.getenv('CDN_BASE_URLS', '').split(',') if u.strip()]
QUEUE_NAME = os.getenv('QUEUE_NAME', 'movie_sending_queue')
REDIS_URL = os.getenv('REDIS_URL')

MOVIES_FILE = 'movies.json'
SUBSCRIPTION_CHECK_INTERVAL = 300
user_subscription_cache = {}

if REDIS_URL:
    redis_conn = Redis.from_url(REDIS_URL)
else:
    redis_conn = Redis(host='localhost', port=6379)
movie_queue = Queue(QUEUE_NAME, connection=redis_conn)

_cdn_rr = itertools.cycle(CDN_BASE_URLS) if CDN_BASE_URLS else None

def _is_url_healthy(url: str, timeout: float = 5.0) -> bool:
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            r = client.head(url)
            if r.status_code >= 400:
                r = client.get(url, headers={'Range': 'bytes=0-0'})
            return 200 <= r.status_code < 400
    except Exception:
        return False

def _choose_cdn_base() -> str | None:
    if not _cdn_rr:
        return None
    try:
        return next(_cdn_rr)
    except Exception:
        return None

def _build_cdn_url(movie_item: dict) -> str | None:
    urls = movie_item.get('urls')
    if isinstance(urls, list) and urls:
        for u in urls:
            if _is_url_healthy(u):
                return u
        return urls[0]
    path = movie_item.get('path')
    base = _choose_cdn_base()
    if base and path:
        if base.endswith('/') and path.startswith('/'):
            return base[:-1] + path
        elif not base.endswith('/') and not path.startswith('/'):
            return base + '/' + path
        else:
            return base + path
    return None

if not BOT_TOKEN:
    logger.critical("BOT_TOKEN topilmadi! .env faylida BOT_TOKEN=... qilib tokenni kiriting.")
    raise SystemExit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='Markdown')

# Flask app for Render health checks
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running! 🚀"

@app.route('/health')
def health():
    return {"status": "ok"}, 200

def run_flask():
    # Render sets the PORT environment variable automatically
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Adminni tekshirish uchun universal funksiya
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS or user_id == 6849709091

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    logger.info(f"Admin panel so'rovi: User ID {user_id}")
    
    if is_admin(user_id):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📢 Kanallarni boshqarish", callback_data="manage_channels"))
        kb.add(types.InlineKeyboardButton("🎬 Kino qo'shish", callback_data="add_movie_start"))
        kb.add(types.InlineKeyboardButton("📊 Statistika", callback_data="admin_stats"))
        
        bot.send_message(chat_id, "👨‍💻 **Admin Panel**\n\nKerakli bo'limni tanlang:", reply_markup=kb)
    else:
        bot.reply_to(message, f"Siz admin emassiz! ❌\nSizning ID: `{user_id}`")

def manage_channels(callback):
    if not is_admin(callback.from_user.id): return
    
    channels, urls = database.get_channels()
    text = "📢 **Majburiy kanallar ro'yxati:**\n\n"
    kb = types.InlineKeyboardMarkup(row_width=2)
    
    for i, (ch, url) in enumerate(zip(channels, urls)):
        text += f"{i+1}. `{ch}`\n"
        kb.add(types.InlineKeyboardButton(f"❌ {i+1}-ni o'chirish", callback_data=f"remove_ch_{i}"))
    
    kb.row(types.InlineKeyboardButton("➕ Kanal qo'shish", callback_data="add_channel_start"))
    kb.row(types.InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_back"))
    
    bot.edit_message_text(text, callback.message.chat.id, callback.message.message_id, reply_markup=kb, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("remove_ch_"))
def remove_channel_callback(callback):
    if not is_admin(callback.from_user.id): return
    index = int(callback.data.split('_')[2])
    if database.remove_channel(index):
        global REQUIRED_CHANNELS, REQUIRED_CHANNEL_URLS
        REQUIRED_CHANNELS, REQUIRED_CHANNEL_URLS = database.get_channels()
        bot.answer_callback_query(callback.id, "Kanal o'chirildi ✅")
        manage_channels(callback)

@bot.callback_query_handler(func=lambda c: c.data == "add_channel_start")
def add_channel_start(callback):
    if not is_admin(callback.from_user.id): return
    msg = bot.send_message(callback.message.chat.id, "Kanal ID va havolasini quyidagi formatda yuboring:\n\n`-1001234567890, https://t.me/kanal_link`")
    bot.register_next_step_handler(msg, process_add_channel)

def process_add_channel(message):
    if not is_admin(message.from_user.id): return
    try:
        ch_id, url = message.text.split(',')
        if database.add_channel(ch_id.strip(), url.strip()):
            global REQUIRED_CHANNELS, REQUIRED_CHANNEL_URLS
            REQUIRED_CHANNELS, REQUIRED_CHANNEL_URLS = database.get_channels()
            bot.send_message(message.chat.id, "Kanal muvaffaqiyatli qo'shildi ✅")
        else:
            bot.send_message(message.chat.id, "Bu kanal allaqachon mavjud ❌")
    except Exception:
        bot.send_message(message.chat.id, "Format xato! Qayta urinib ko'ring ❌")

@bot.callback_query_handler(func=lambda c: c.data == "add_movie_start")
def add_movie_start(callback):
    if not is_admin(callback.from_user.id): return
    msg = bot.send_message(callback.message.chat.id, "Kino ma'lumotlarini quyidagi formatda yuboring:\n\n`kod, fayl_id, sarlavha`\n\nMasalan:\n`101, BAACAgIA..., Qasoskorlar`")
    bot.register_next_step_handler(msg, process_add_movie)

def process_add_movie(message):
    try:
        parts = message.text.split(',')
        code = parts[0].strip()
        file_id = parts[1].strip()
        caption = parts[2].strip()
        
        database.add_movie(code, 'video', file_id=file_id, caption=caption)
        bot.send_message(message.chat.id, f"Kino qo'shildi ✅\nKodi: `{code}`")
    except Exception:
        bot.send_message(message.chat.id, "Format xato! Qayta urinib ko'ring ❌")

@bot.callback_query_handler(func=lambda c: c.data == "admin_back")
def admin_back(callback):
    admin_panel(callback.message)

@bot.callback_query_handler(func=lambda c: c.data == "admin_stats")
def admin_stats_callback(callback):
    movie_count, user_count = database.get_stats()
    text = f"📊 **Bot Statistikasi:**\n\n🎬 Jami filmlar: {movie_count}\n👥 Jami foydalanuvchilar: {user_count}"
    bot.edit_message_text(text, callback.message.chat.id, callback.message.message_id, reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⬅️ Orqaga", callback_data="admin_back")))

@bot.message_handler(commands=['start'])
def cmd_start(message):
    user = message.from_user
    database.add_user(user.id, user.username, f"{user.first_name} {user.last_name or ''}".strip())
    
    kb = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for i, url in enumerate(REQUIRED_CHANNEL_URLS):
        if url.strip():
            buttons.append(types.InlineKeyboardButton(text=f"📢 {i+1}-kanal", url=url.strip()))
    
    if buttons:
        kb.add(*buttons)
    
    kb.row(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subscription"))
    
    bot.send_message(
        message.chat.id,
        f"Salom {user.first_name}! 👋\n\n"
        "🎬 Kino botiga xush kelibsiz!\n"
        "Kino kodlarini yuboring va kinolarni oling.\n\n"
        "ℹ️ Botdan foydalanish uchun quyidagi kanallarga a'zo bo'lishingiz kerak:",
        reply_markup=kb
    )

@bot.callback_query_handler(func=lambda c: c.data == "check_subscription")
def on_check_subscription(callback):
    user_id = callback.from_user.id
    not_subscribed = []
    
    logger.info(f"🔍 Professional obuna tekshiruvi: User {user_id}")
    
    # Kanallarni bazadan yangilab olamiz (har ehtimolga qarshi)
    channels, _ = database.get_channels()
    
    for ch_id in channels:
        ch_id = ch_id.strip()
        if not ch_id: continue
        
        try:
            # ID ni songa o'tkazish (Telegram ID lari son bo'lishi kerak)
            target_id = int(ch_id) if ch_id.replace('-', '').isdigit() else ch_id
            
            member = bot.get_chat_member(target_id, user_id)
            status = getattr(member, "status", None)
            
            logger.info(f"📊 Kanal {ch_id} | Status: {status}")
            
            if status not in ['member', 'administrator', 'creator']:
                not_subscribed.append(ch_id)
        except Exception as e:
            logger.error(f"⚠️ Kanal {ch_id} tekshirishda API xatolik: {e}")
            # Agar bot kanalda bo'lmasa yoki admin bo'lmasa, bu yerda xatolik chiqadi
            not_subscribed.append(ch_id)

    if not not_subscribed:
        try:
            user_subscription_cache[user_id] = time.time()
            bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text="✅ **Tabriklaymiz!**\n\nSiz barcha majburiy kanallarga muvaffaqiyatli a'zo bo'ldingiz. Endi botdan cheksiz foydalanishingiz mumkin!\n\n🎬 **Kino kodini yuboring:**"
            )
        except Exception:
            bot.answer_callback_query(callback.id, "✅ Hammasi joyida! Kino kodini yuboring.", show_alert=True)
    else:
        # Qaysi kanalga a'zo bo'lmaganini aniqlash
        bot.answer_callback_query(
            callback.id, 
            "❌ Xatolik! Siz hali barcha kanallarga a'zo bo'lmadingiz yoki bot u kanallarda admin emas.\n\nIltimos, qayta tekshiring!", 
            show_alert=True
        )

def is_subscribed(user_id: int) -> bool:
    # Adminlar uchun har doim ruxsat (debug va test uchun)
    if is_admin(user_id):
        return True
        
    current_time = time.time()
    if user_id in user_subscription_cache and (current_time - user_subscription_cache[user_id]) < SUBSCRIPTION_CHECK_INTERVAL:
        return True
        
    channels, _ = database.get_channels()
    for ch_id in channels:
        ch_id = ch_id.strip()
        if not ch_id: continue
        
        try:
            target_id = int(ch_id) if ch_id.replace('-', '').isdigit() else ch_id
            member = bot.get_chat_member(target_id, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            logger.error(f"🚫 is_subscribed API Error ({ch_id}): {e}")
            return False
            
    user_subscription_cache[user_id] = current_time
    return True

@bot.message_handler(content_types=['video', 'document'])
def get_file_id(message):
    try:
        if message.video:
            file_id = message.video.file_id
            bot.send_message(message.chat.id, f"✅ Video qabul qilindi!\n\nFile ID: `{file_id}`\n\nEndi shu ID ni va kino kodini menga yuboring.")
        elif message.document:
            file_id = message.document.file_id
            bot.send_message(message.chat.id, f"✅ Fayl qabul qilindi!\n\nFile ID: `{file_id}`\n\nEndi shu ID ni va kino kodini menga yuboring.")
        else:
            bot.send_message(message.chat.id, "❌ Media turi aniqlanmadi. Iltimos, video yoki hujjat yuboring.")
    except Exception as e:
        logger.error(f"Media xabarini qayta ishlashda xatolik: {e}")
        bot.send_message(message.chat.id, "❌ Media xabarini qayta ishlashda kutilmagan xatolik yuz berdi.")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    movie_count, user_count = database.get_stats()
    bot.send_message(
        message.chat.id, 
        f"📊 **Bot Statistikasi:**\n\n"
        f"🎬 Jami filmlar: {movie_count}\n"
        f"👥 Jami foydalanuvchilar: {user_count}\n"
        f"✅ Bot hozirda faol."
    )

@bot.message_handler(func=lambda m: m.content_type == 'text')
def handle_text(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if not is_subscribed(user_id):
        kb = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for i, url in enumerate(REQUIRED_CHANNEL_URLS):
            if url.strip():
                buttons.append(types.InlineKeyboardButton(text=f"📢 {i+1}-kanal", url=url.strip()))
        
        if buttons:
            kb.add(*buttons)
            
        kb.row(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subscription"))
        
        bot.send_message(
            message.chat.id,
            "❌ Kino olish uchun avval kanallarga a'zo bo'lishingiz kerak!\n"
            "Quyidagi kanallarga a'zo bo'ling va 'Tekshirish' tugmasini bosing:",
            reply_markup=kb
        )
        return

    movies = database.get_movie_by_code(text)
    if movies:
        for movie_item in movies:
            _send_movie(message, movie_item)
    else:
        # Fuzzy matching logic
        codes = database.get_all_codes()
        matches = difflib.get_close_matches(text, codes, n=3, cutoff=0.6)
        
        error_msg = f"❌ Kechirasiz, `{text}` kodi bo'yicha hech qanday film topilmadi."
        if matches:
            suggestions = "\n".join([f"🔹 `{m}`" for m in matches])
            error_msg += f"\n\nBalki shulardan birini nazarda tutgandirsiz:\n{suggestions}"
        
        bot.send_message(message.chat.id, error_msg)

def _send_movie(message, movie_item):
    m_type = movie_item['type']
    caption = movie_item['caption'] or "Kino"
    
    if m_type == 'text':
        bot.send_message(
            message.chat.id,
            f"🎬 {caption}\n\n"
            f"🔗 Link: {movie_item['url'] or movie_item['path']}"
        )
    elif m_type == 'video':
        try:
            bot.send_video(
                message.chat.id,
                movie_item['file_id'],
                caption=caption
            )
            bot.send_message(message.chat.id, "✅ Kino yuborildi.")
        except Exception as e:
            logger.error(f"Vazifa navbatga qo'yilmadi: {e}")
            try:
                movie_queue.enqueue(
                    send_video_task,
                    chat_id=message.chat.id,
                    video_file_id=movie_item['file_id'],
                    caption=caption
                )
                bot.send_message(message.chat.id, "ℹ️ Kino navbatga qo'yildi. Bir ozdan so'ng yetkaziladi.")
            except Exception as ee:
                logger.error(f"Bevosita yuborishda ham xatolik: {ee}")
                bot.send_message(message.chat.id, "❌ Kino yuborishda kutilmagan xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
    elif m_type == 'cdn' or m_type == 'text_multi':
        url = movie_item['url'] or _build_cdn_url(dict(movie_item))
        if url:
            bot.send_message(
                message.chat.id,
                f"🎬 {caption}\n\n"
                f"🔗 Link: {url}"
            )
        else:
            bot.send_message(message.chat.id, "❌ Linkni aniqlab bo'lmadi.")
    else:
        bot.send_message(message.chat.id, "❌ Noma'lum kino turi!")

if __name__ == "__main__":
    try:
        logger.info("Flask server start bo'lyapti (Render health checks uchun).")
        threading.Thread(target=run_flask, daemon=True).start()
        
        logger.info("Bot start oldi (TeleBot).")
        bot.infinity_polling(timeout=20, long_polling_timeout=20, allowed_updates=['message', 'callback_query'])
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi (KeyboardInterrupt).")
    except SystemExit:
        logger.info("Bot to'xtatildi (SystemExit).")
