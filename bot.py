import os
import sys
import logging
import asyncio
import random
import discord
from discord.ext import tasks

# 1. Konsol ve Log Yapılandırması (Railway loglarında temiz görünür)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 2. Ortam Değişkenlerini Yükleme ve Doğrulama
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID_RAW = os.getenv('CHANNEL_ID')
MESSAGE = os.getenv('MESSAGE', 'Bu otomatik bir bilgilendirme mesajıdır.')
INTERVAL_HOURS = float(os.getenv('INTERVAL_HOURS', '1.5'))

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


# 3. Dayanıklı Self-Bot Sınıfı
class RobustSelfBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        logging.info(f"Oturum başarıyla açıldı: {self.user} (ID: {self.user.id})")
        if not self.saatlik_gorev.is_running():
            self.saatlik_gorev.start()

    async def on_disconnect(self):
        logging.warning("Discord bağlantısı koptu. Otomatik yeniden bağlanma bekleniyor...")

    async def on_resumed(self):
        logging.info("Discord bağlantısı başarıyla tekrar sağlandı.")

    # Saatlik Döngü Görevi
    @tasks.loop(hours=INTERVAL_HOURS)
    async def saatlik_gorev(self):
        try:
            # Önce önbelleğe bak, bulamazsa API'den çek
            channel = self.get_channel(CHANNEL_ID)
            if channel is None:
                logging.info("Kanal önbellekte bulunamadı, API üzerinden çekiliyor...")
                channel = await self.fetch_channel(CHANNEL_ID)

            # İnsan benzeri davranış için 20 - 90 saniye arası rastgele gecikme
            jitter = random.randint(20, 90)
            logging.info(f"Görev zamanı geldi. {jitter} saniyelik rastgele bekleme uygulanıyor...")
            await asyncio.sleep(jitter)

            # Mesajı gönder
            await channel.send(MESSAGE)
            logging.info(f"SUCCESS: Mesaj gönderildi -> Kanal ID: {CHANNEL_ID}")

        except discord.Forbidden:
            logging.error(f"HATA: Bu kanala mesaj atma yetkiniz yok! (Kanal ID: {CHANNEL_ID})")
        except discord.NotFound:
            logging.error(f"HATA: Belirtilen ID ile kanal bulunamadı! (Kanal ID: {CHANNEL_ID})")
        except discord.HTTPException as e:
            logging.error(f"HATA: Discord HTTP İsteği başarısız oldu: {e}")
        except Exception as e:
            logging.error(f"BEKLENMEYEN HATA: {e}")

    @saatlik_gorev.before_loop
    async def before_saatlik_gorev(self):
        # Bot tamamen hazır olana kadar döngüyü başlatma
        await self.wait_until_ready()

# 4. Uygulamayı Başlatma
if __name__ == "__main__":
    client = RobustSelfBot()
    try:
        client.run(TOKEN)
    except discord.LoginFailure:
        logging.critical("KRİTİK: Giriş başarısız! Token geçersiz veya sıfırlanmış.")
    except Exception as e:
        logging.critical(f"KRİTİK: Başlatma hatası: {e}")
