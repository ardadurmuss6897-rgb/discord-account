import os
import sys
import logging
import asyncio
import random
import datetime
import discord
from discord.ext import tasks

# ==========================================
# 🎯 1. BÖLÜM: BİLGİ VE SPOTIFY AYARLARI
# ==========================================

# 🎵 Profilde Görünecek Spotify Şarkı Bilgileri
SPOTIFY_TITLE = "Cevapsız Sorular"
SPOTIFY_ARTIST = "maNga"
SPOTIFY_ALBUM = "maNga"
# Spotify şarkı linkindeki track/ sonrası gelen ID kopyalanmalıdır
SPOTIFY_TRACK_ID = "38aAwEQ0g0k65V00U1sS4v" 
SONG_DURATION_SECONDS = 272  # 4 dakika 32 saniye = 272 saniye

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
    logging.critical("KRİTİK HATA: 'DISCORD_TOKEN' veya 'CHANNEL_ID' değişkeni eksik!")
    sys.exit(1)

try:
    CHANNEL_ID = int(CHANNEL_ID_RAW)
except ValueError:
    logging.critical("KRİTİK HATA: 'CHANNEL_ID' sadece sayılardan oluşmalıdır!")
    sys.exit(1)

# ==========================================
# 🚀 3. BÖLÜM: GELİŞMİŞ SELF-BOT SINIFI
# ==========================================

class MasterSelfBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        logging.info(f"Oturum açıldı: {self.user} (ID: {self.user.id})")
        
        # Görevleri Başlatma
        if not self.saatlik_gorev.is_running():
            self.saatlik_gorev.start()
        if not self.spotify_dogrusu.is_running():
            self.spotify_dogrusu.start()

    async def on_disconnect(self):
        logging.warning("Discord bağlantısı koptu, otomatik yeniden bağlanılacak...")

    async def on_resumed(self):
        logging.info("Discord bağlantısı yeniden kuruldu.")

    # 🕒 Görev 1: Periyodik Mesaj Gönderme
    @tasks.loop(hours=INTERVAL_HOURS)
    async def saatlik_gorev(self):
        try:
            channel = self.get_channel(CHANNEL_ID)
            if channel is None:
                channel = await self.fetch_channel(CHANNEL_ID)

            # Anti-Spam Güvenliği için 20 - 90s arası rastgele bekleme
            jitter = random.randint(20, 90)
            logging.info(f"Mesaj zamanı geldi. {jitter} saniye bekleniyor...")
            await asyncio.sleep(jitter)

            await channel.send(MESSAGE)
            logging.info(f"BAŞARILI: Mesaj gönderildi -> Kanal ID: {CHANNEL_ID}")

        except discord.Forbidden:
            logging.error("HATA: Bu kanalda mesaj atma yetkisi yok!")
        except discord.NotFound:
            logging.error("HATA: Kanal ID bulunamadı!")
        except Exception as e:
            logging.error(f"Mesaj gönderme hatası: {e}")

    @saatlik_gorev.before_loop
    async def before_saatlik_gorev(self):
        await self.wait_until_ready()

    # 🎵 Görev 2: Spotify Canlı Zaman Çubuğu Döngüsü
    @tasks.loop(seconds=SONG_DURATION_SECONDS)
    async def spotify_dogrusu(self):
        try:
            start_time = datetime.datetime.now(datetime.timezone.utc)
            end_time = start_time + datetime.timedelta(seconds=SONG_DURATION_SECONDS)

            spotify_act = discord.Spotify(
                title=SPOTIFY_TITLE,
                artist=SPOTIFY_ARTIST,
                album=SPOTIFY_ALBUM,
                track_id=SPOTIFY_TRACK_ID,
                start=start_time,
                end=end_time
            )
            await self.change_presence(activity=spotify_act)
            logging.info(f"Spotify Durumu Yenilendi: '{SPOTIFY_ARTIST} - {SPOTIFY_TITLE}'")
        except Exception as e:
            logging.error(f"Spotify durumu güncellenirken hata: {e}")

    @spotify_dogrusu.before_loop
    async def before_spotify_dogrusu(self):
        await self.wait_until_ready()

# ==========================================
# 🏁 4. BÖLÜM: ÇALIŞTIRMA
# ==========================================

if __name__ == "__main__":
    client = MasterSelfBot()
    try:
        client.run(TOKEN)
    except discord.LoginFailure:
        logging.critical("KRİTİK HATA: Token geçersiz veya sıfırlanmış!")
    except Exception as e:
        logging.critical(f"Çalıştırma hatası: {e}")
