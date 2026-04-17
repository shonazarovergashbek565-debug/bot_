# Telegram Kino Bot - Professional Edition

Bu bot Telegram orqali kino kodlarini yuborib, kinolarni olishingiz mumkin. Bot profesyonel, nuhsonsiz va tarmoq muammolariga chidamli.

## Xususiyatlari

### 🛡️ Chidamli Tarmoq Ulashuvi
- **Exponential Backoff** strategiyasi - tarmoq muammolarida avtomatik qayta urinishlar
- **Jitter Mexanizmi** - server yukini kamaytirish uchun tasodifiy kechikishlar
- **Katta Timeoutlar** - uzoq vaqtli tarmoq ulanishlariga chidamlilik
- **Avto Restart** - bot tushsa ham avtomatik qayta ishga tushadi

### 📊 Batafsil Loglash
- **Fayl va Ekran** loglari - barcha hodisalar saqlanadi
- **Bosqichma-Bosqich Loglar** - har bir operatsiya tafsilotlari
- **Xatoliklarni Tafsilotli Tasvirlash** - debug qilish uchun qulay
- **Kutilmaganda To'xtashlarni Kuzatish** - bot muammolarini aniqlash

### 🔒 Xavfsizlik va Qo'llanilish
- **Kanal A'zoligini Tekshirish** - faqat kanal a'zolari foydalanishi mumkin
- **Atrof-Muhit O'zgaruvchilari** - token va kanal sozlamalari xavfsiz saqlanadi
- **Auto Restart Mexanizmi** - bat skripti orqali doimiy ishga tushirish

### 💪 Professional Dizayn
- **Modulyar Tuzilma** - kodni oson tahrirlash va kengaytirish
- **Kengaytiriladigan Arxitektura** - yangi funksiyalar qo'shish oson
- **Standartlarga Amal qilish** - Python best practices
- **Testlash va Debug** - muammolarni oson topish va tuzatish

## Yordam

### 1. Botni Ishga Tushirish

#### Oddiy Ishga Tushirish
```bash
python main.py
```

#### Professional Ishga Tushirish (Auto Restart)
```bash
.\run_bot_pro.bat
```

#### Oddiy Ishga Tushirish (Bat Skripti)
```bash
.\run_bot.bat
```

### 2. Sozlamalar

#### .env Fayli
Botning asosiy sozlamalari `.env` faylida saqlanadi:

```env
# Bot Token - @BotFather dan oling
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN

# Kerakli Kanallar (Foydalanuvchilar bu kanallarga a'zo bo'lishlari kerak)
REQUIRED_CHANNELS=@kulgu_178

# Kanallar uchun URL lar (Botda ko'rsatiladigan havolalar)
REQUIRED_CHANNEL_URLS=https://t.me/kulgu_178

# Proxy URL (Iltimos, kerak bo'lsa o'zingizning proxy URL ingizni yozing)
# PROXY_URL=socks5://proxy.example.com:1080
```

### 3. Filmlarni Qo'shish

Filmlar `movies.json` faylida saqlanadi. Har bir film uchun quyidagi formatdan foydalaning:

```json
{
  "1": {
    "type": "video",
    "file_id": "BAACAgIAAxkBAAIEVml3eUSkOUwsa5wxRKYqSfSgIle0AAK_dwACzqagSFLMMe5ZZ1hWOAQ",
    "caption": "Film Nomi (Yil)"
  },
  "2": {
    "type": "text",
    "text": "https://example.com/film-link",
    "caption": "Film Nomi (Yil)"
  }
}
```

#### Film Tipi
- `video` - Telegram video file ID si
- `text` - Har qanday matn yoki havola

### 4. Botni Remote Serverda Host qilish

Botni doimiy ravishda ishga tushirish uchun remote serverdan foydalaning. Quyidagi qadamlarni bajaring:

#### 4.1 Server Tanlash (VPS Tavsiya etiladi 🚀)

Eng barqaror va professional yo'l - bu **VPS (Virtual Private Server)** dan foydalanish:
- **DigitalOcean** - Dropletlar, juda oson va ishonchli.
- **Hetzner Cloud** - Arzon va kuchli serverlar.
- **VDS.ir / AWS / Google Cloud** - Istalgan Ubuntu o'rnatilgan server.

#### 4.2 VPS Serverda Docker orqali ishga tushirish (Eng xavfsiz va tez yo'l)

1. **SSH orqali serverga ulaning**:
   ```bash
   ssh root@your-server-ip
   ```

2. **Docker va Docker Compose o'rnatish**:
   ```bash
   curl -fsSL https://get.docker.com | sh
   apt install docker-compose-plugin -y
   ```

3. **Loyiha fayllarini yuklash**:
   GitHub'dan klon qiling yoki fayllarni serverga yuboring:
   ```bash
   git clone https://github.com/your-username/telegram-kino-bot.git
   cd telegram-kino-bot
   ```

4. **.env faylini yaratish**:
   ```bash
   nano .env
   ```
   Ichiga quyidagilarni yozing:
   ```env
   BOT_TOKEN=Sizning_Bot_Tokeningiz
   REQUIRED_CHANNELS=@kanal_nomi
   REQUIRED_CHANNEL_URLS=https://t.me/kanal_nomi
   ```

5. **Docker Compose orqali ishga tushirish**:
   ```bash
   docker compose up -d --build
   ```

6. **Holatni tekshirish**:
   ```bash
   docker compose ps
   docker compose logs -f bot
   ```

#### 4.3 Nima uchun Docker?
- **Restart**: Agar bot yoki server o'chib qolsa, Docker uni avtomatik qayta yoqadi (`restart: unless-stopped`).
- **Redis**: Redis serverini o'rnatish shart emas, u konteyner ichida tayyor keladi.
- **Xavfsizlik**: Bot boshqa sistema fayllaridan ajratilgan holda ishlaydi.

1. **SSH orqali serverga ulaning**:
   ```bash
   ssh root@your-server-ip
   ```

2. **Sistema yangilash**:
   ```bash
   apt update && apt upgrade -y
   ```

3. **Python o'rnatish**:
   ```bash
   apt install python3 python3-pip python3-venv -y
   ```

4. **Git o'rnatish**:
   ```bash
   apt install git -y
   ```

5. **Bot kodlarini olish**:
   ```bash
   mkdir -p /opt/telegram-bot
   cd /opt/telegram-bot
   git clone https://github.com/your-username/telegram-kino-bot.git .
   ```

6. **Virtual muhit yaratish**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

7. **Qurilmalarni o'rnatish**:
   ```bash
   pip install -r requirements.txt
   ```

8. **.env faylini yaratish**:
   ```bash
   nano .env
   ```
   `.env` fayliga o'zingizning bot tokeningiz va kanal sozlamalarini yozing.

9. **Systemd xizmatini yaratish** (auto restart uchun):
   ```bash
   nano /etc/systemd/system/telegram-kino-bot.service
   ```

   Pastdagi kontentni yozing (o'zingizning yo'llarni o'zgartiring):
   ```ini
   [Unit]
   Description=Telegram Kino Bot
   After=network.target
   
   [Service]
   Type=simple
   User=root
   WorkingDirectory=/opt/telegram-bot
   ExecStart=/opt/telegram-bot/venv/bin/python main.py
   Restart=always
   RestartSec=5
   Environment=PYTHONUNBUFFERED=1
   
   [Install]
   WantedBy=multi-user.target
   ```

10. **Systemd xizmatini ishga tushirish**:
    ```bash
    systemctl daemon-reload
    systemctl enable telegram-kino-bot
    systemctl start telegram-kino-bot
    ```

11. **Xizmat holatini tekshirish**:
    ```bash
    systemctl status telegram-kino-bot
    ```

12. **Loglarni ko'rish**:
    ```bash
    journalctl -u telegram-kino-bot -f
    ```

#### 4.3 Serverda Botni Monitoring qilish

1. **Loglarni real vaqtda ko'rish**:
   ```bash
   tail -f /opt/telegram-bot/bot.log
   ```

2. **Bot holatini tekshirish**:
   ```bash
   systemctl status telegram-kino-bot
   ```

3. **Botni qayta ishga tushirish**:
   ```bash
   systemctl restart telegram-kino-bot
   ```

4. **Botni to'xtatish**:
   ```bash
   systemctl stop telegram-kino-bot
   ```

### 5. Best Practices

#### 📌 Qo'llanilish Maslahatlari
1. **VPN Foydalaning** - Agar server tarmog'ida Telegram API ni ochiq bo'lmasa, VPN foydalaning
2. **Regular Backup** - `movies.json` va `.env` fayllarini regular ravishda backup qiling
3. **Loglarni Tozalash** - Bot loglari katta bo'lganida, ularni tozalang yoki arxivlang
4. **Botni Yangilash** - Yangi versiyalarni tezda o'rnating

#### 🔧 Debug Maslahatlari
1. **Loglarni Tekshiring** - Bot muammosi bo'lsa, avval `bot.log` faylini tekshiring
2. **Test Conn Scripti** - `test_conn.py` yordamida Telegram API ulanishini tekshiring
3. **Virtual Muhit** - Botni virtual muhit ichida ishlating
4. **Systemd Loglari** - Serverda bo'lsa, systemd loglarini tekshiring

### 6. Botni Qo'shimcha Funksiyalar bilan Kengaytirish

#### Yangi Handler qo'shish
```python
async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Yangi komanda logikasi
    await update.message.reply_text("Yangi komanda!")

# Handlerni qo'shish
application.add_handler(CommandHandler("new", new_command))
```

#### Yangi Filter qo'shish
```python
# Faqat adminlarga ruxsat beruvchi filter
async def admin_filter(update: Update):
    user_id = update.effective_user.id
    return user_id in [123456789, 987654321]

# Filter bilan handler
application.add_handler(CommandHandler("admin", admin_command, filters=filters.create(admin_filter)))
```

### 7. Dasturiy Ta'minotlar

- **Python 3.8+** - Botni ishga tushirish uchun
- **python-telegram-bot v22.5** - Telegram API bilan ishlash uchun
- **python-dotenv** - Atrof-muhit o'zgaruvchilarini o'qish uchun
- **httpx** - HTTP so'rovlari uchun

### 8. Troubleshooting

#### Umumiy Muammolar va Yechimlari

1. **Bot ishlamayotgan holat**:
   - `.env` faylidagi token to'g'ri ekanligini tekshiring
   - Kanal nomi va URL lar to'g'ri ekanligini tekshiring
   - Log faylini tekshiring: `tail -f bot.log`
   - Test conn scripti ishga tushiring: `python test_conn.py`

2. **Tarmoq Muammolari**:
   - VPN o'rnatib ko'ring
   - `.env` fayliga proxy qo'shing
   - Server ulanishini tekshiring: `ping api.telegram.org`

3. **Bot qayta ishga tushmayotgan holat**:
   - Systemd xizmatini tekshiring: `systemctl status telegram-kino-bot`
   - `.env` faylidagi sozlamalar to'g'ri ekanligini tekshiring
   - Python versiyasini tekshiring: `python --version`

4. **Kanal A'zoligini Tekshirishda Xatolik**:
   - Kanal nomi to'g'ri ekanligini tekshiring (masalan: @kulgu_178)
   - Bot kanalga admin sifatida qo'shilganligini tekshiring
   - Kanal ochiq ekanligini tekshiring

### 9. Litsenziya

Bu bot MIT litsenziyasi ostida tarqatiladi. Batafsil ma'lumot uchun `LICENSE` faylini ko'ring.

### 10. Bog'lanish

Agar botda muammo bo'lsa yoki takliflaringiz bo'lsa, quyidagi yo'llar orqali bog'laning:

- **Telegram** - @your-username
- **GitHub** - https://github.com/your-username/telegram-kino-bot
- **Email** - your.email@example.com

---

**Bot Professional Edition - Doimiy Ish, Nuhsonsiz Vaqtinchalik Muammolarni Boshqarish** 🚀
