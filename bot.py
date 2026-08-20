import os
import sys
import logging
import asyncio
import random
import datetime
import discord
from discord.ext import tasks

# ==========================================
# 🎯 1. BÖLÜM: SPOTIFY PLAYLIST VE AYARLAR
# ==========================================

# 🎵 Kendi Şarkılarını Buraya Ekle (Sırayla değişecek)
PLAYLIST = [
    {
        "title": "Cevapsız Sorular",
        "artists": ["maNga"],
        "album": "maNga",
        "track_id": "38aAwEQ0g0k65V00U1sS4v",
        "duration": 272  
    },
    {
        "title": "Bir Kadın Çizeceksin",
        "artists": ["maNga"],
        "album": "maNga",
        "track_id": "2M2E4hU2D1FwZzGnbC36Za", 
        "duration": 238  
    }
]

# 📢 Kanala Atılacak Duyuru Metni
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

# ==========================================
# ⚙️ 2. BÖLÜM: SİSTEM VE LOG YAPILANDIRMASI
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID_RAW = os.getenv('CHANNEL_ID')
INTERVAL_HOURS = float(os.getenv('INTERVAL_HOURS', '1.5'))

if not TOKEN or not CHANNEL_ID_RAW:
    logging.critical("KRİTİK HATA: 'DISCORD_TOKEN' veya 'CHANNEL_ID' eksik!")
    sys.exit(1)

CHANNEL_ID = int(CHANNEL_ID_RAW)

# ==========================================
# 🚀 3. BÖLÜM: GELİŞMİŞ SELF-BOT SINIFI
# ==========================================

class MasterSelfBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        logging.info(f"Oturum açıldı: {self.user} (ID: {self.user.id})")
        
        self.loop.create_task(self.spotify_dongusu())
        if not self.saatlik_gorev.is_running():
            self.saatlik_gorev.start()

    async def on_disconnect(self):
        logging.warning("Discord bağlantısı koptu, yeniden bağlanılacak...")

    @tasks.loop(hours=INTERVAL_HOURS)
    async def saatlik_gorev(self):
        try:
            channel = self.get_channel(CHANNEL_ID) or await self.fetch_channel(CHANNEL_ID)
            jitter = random.randint(20, 90)
            await asyncio.sleep(jitter)
            await channel.send(MESSAGE)
            logging.info(f"BAŞARILI: Mesaj atıldı -> Kanal ID: {CHANNEL_ID}")
        except Exception as e:
            logging.error(f"Mesaj atılamadı: {e}")

    @saatlik_gorev.before_loop
    async def before_saatlik_gorev(self):
        await self.wait_until_ready()

    # 🎵 Görev 2: Spotify Playlist Döngüsü
    async def spotify_dongusu(self):
        await self.wait_until_ready()
        index = 0
        while not self.is_closed():
            try:
                sarki = PLAYLIST[index]
                start_time = datetime.datetime.now(datetime.timezone.utc)
                end_time = start_time + datetime.timedelta(seconds=sarki["duration"])

                # ADIM 1: Zaman parametreleri olmadan sadece şarkı bilgileriyle objeyi oluşturuyoruz
                spotify_act = discord.Spotify(
                    title=sarki["title"],
                    artists=sarki["artists"],
                    album=sarki["album"],
                    track_id=sarki["track_id"]
                )
                
                # ADIM 2: Kütüphanenin arka planda kullandığı gizli değişkenlere süreyi dışarıdan müdahaleyle ekliyoruz
                spotify_act._start = start_time
                spotify_act._end = end_time

                await self.change_presence(activity=spotify_act)
                logging.info(f"🎵 Çalıyor: {sarki['artists'][0]} - {sarki['title']}")

                # Şarkı süresi kadar arka planda bekle
                await asyncio.sleep(sarki["duration"])

                # Sıradaki şarkıya geç
                index = (index + 1) % len(PLAYLIST)

            except Exception as e:
                logging.error(f"Spotify döngüsü hatası: {e}")
                await asyncio.sleep(15)

if __name__ == "__main__":
    client = MasterSelfBot()
    client.run(TOKEN)
