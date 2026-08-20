import os
import sys
import logging
import asyncio
import random
import discord
from discord.ext import tasks

# 1. Konsol ve Log Yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 2. Ortam Değişkenleri ve Çok Satırlı Mesaj
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID_RAW = os.getenv('CHANNEL_ID')
INTERVAL_HOURS = float(os.getenv('INTERVAL_HOURS', '1.0'))

# Mesajı Railway'den değil, doğrudan buradan üç tırnak (multi-line) ile veriyoruz
MESSAGE = """▬▬▬▬▬▬๑ 𝐒𝐎𝐍 𝐀𝐋𝐅𝐀𝐋𝐀𝐑 ๑▬▬▬▬▬▬●
[♛] ┊ Sıra : 3
[✩] ┊ ÖZEL LOGO
[✩] ┊ Aylık Birincilik
[✩] ┊ Haftalık Birincilik
[✩] ┊ Safranbolu Birincilik
[✩] ┊ Diğer Haritalarda 10. Sırada 
[✩] ┊ 2800+ Kişilik Sunucu
●▬▬▬๑ 𝐎𝐍𝐂𝐄𝐋𝐈𝐊𝐋𝐈 𝐒𝐀𝐑𝐓𝐋𝐀𝐑 ๑▬▬▬●
[⮚] ┊ Level: Bakılmıyor.
[⮚] ┊ Rank: Zümrüt ve Üzeri.
[⮚] ┊ Yaş: Sınır Yoktur.
[⮚] ┊ Aktif Olan Her Gün Sese Gelen.
[⮚] ┊ Ses Kasmasını Bilen.
[⮚] ┊ Mikrofonu Olan.
[⮚] ┊ Saygısızlık Yapmayan. 
[⮚] ┊ İnfo ve Bomba Taktiklerini Bilen. 
●▬▬▬▬▬▬๑ & ๑▬▬▬▬▬▬●
[➪] ┊ Aktif Rekabet & Klan Savaşı Oyuncu Alımlarımız Devam Ediyor.
[➪] ┊ Çekilişlerimiz Mevcut.
[➪] ┊ Kız oyuncu alımlarımız vardır.
[➪] ┊ İLETİŞİM İÇİN DM"""

if not TOKEN:
    logging.critical("KRİTİK: 'DISCORD_TOKEN' değişkeni bulunamadı! Program kapatılıyor.")
    sys.exit(1)

if not CHANNEL_ID_RAW:
    logging.critical("KRİTİK: 'CHANNEL_ID' değişkeni bulunamadı! Program kapatılıyor.")
    sys.exit(1)

try:
    CHANNEL_ID = int(CHANNEL_ID_RAW)
except ValueError:
    logging.critical("KRİTİK: 'CHANNEL_ID' sadece sayılardan oluşmalıdır!")
    sys.exit(1)

# --- Kodun geri kalanı (3. Dayanıklı Self-Bot Sınıfı kısmı) aynı şekilde aşağıda devam edecek ---
