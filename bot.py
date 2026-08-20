import os
import sys
import logging
import asyncio
import random
import discord
from discord.ext import tasks

# ==========================================
# 🎯 1. BÖLÜM: MESAJ METNİ VE DUYURU AYARI
# ==========================================

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
    logging.critical("KRİTİK HATA: 'DISCORD_TOKEN' veya 'CHANNEL_ID' eksik! Program sonlandırılıyor.")
    sys.exit(1)

try:
    CHANNEL_ID = int(CHANNEL_ID_RAW)
except ValueError:
    logging.critical("KRİTİK HATA: 'CHANNEL_ID' geçerli bir sayı olmalıdır!")
    sys.exit(1)

# ==========================================
# 🚀 3. BÖLÜM: ZIRHLI SELF-BOT MİMARİSİ
# ==========================================

class MasterSelfBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        logging.info(f"Oturum başarıyla açıldı: {self.user} (ID: {self.user.id})")
        
        # Periyodik mesaj döngüsünü başlat
        if not self.saatlik_gorev.is_running():
            self.saatlik_gorev.start()

    async def on_disconnect(self):
        logging.warning("Discord ağ bağlantısı kesildi. Otomatik yeniden bağlanma bekleniyor...")

    @tasks.loop(hours=INTERVAL_HOURS)
    async def saatlik_gorev(self):
        try:
            # Önce kanalı bul
            channel = self.get_channel(CHANNEL_ID)
            if channel is None:
                channel = await self.fetch_channel(CHANNEL_ID)

            # Anti-Spam Koruması (20-90 sn bekle)
            jitter = random.randint(20, 90)
            logging.info(f"Duyuru atılıyor. Anti-spam için {jitter} saniye bekleniyor...")
            await asyncio.sleep(jitter)

            # Yeni Mesajı Gönder (Eskilere dokunmaz)
            await channel.send(MESSAGE)
            logging.info(f"✅ BAŞARILI: Yeni duyuru mesajı gönderildi -> Kanal ID: {CHANNEL_ID}")

        except Exception as e:
            logging.error(f"BEKLENMEYEN HATA: {e}")

    @saatlik_gorev.before_loop
    async def before_saatlik_gorev(self):
        # Bot tamamen hazır olana kadar bekle
        await self.wait_until_ready()
        
        # SİSTEM BAŞLADIĞINDA İLK BEKLEME SÜRESİ
        bekleme_saniyesi = int(INTERVAL_HOURS * 3600)
        logging.info(f"⏳ SİSTEM AKTİF! İlk mesaj atılmadan önce tam {INTERVAL_HOURS} saat ({bekleme_saniyesi} saniye) bekleniyor...")
        await asyncio.sleep(bekleme_saniyesi)

# ==========================================
# 🏁 4. BÖLÜM: BOTA START VERME
# ==========================================

if __name__ == "__main__":
    client = MasterSelfBot()
    try:
        client.run(TOKEN)
    except Exception as e:
        logging.critical(f"BAŞLATMA HATASI: {e}")
