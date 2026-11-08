import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Ajuste dinámico de rutas para poder importar el backend sin errores
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.telegram_bot import run_telegram_bot, CyberGuardianTelegramBot

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("cyberguardian.telegram_bot.main")

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("❌ ERROR: No se encontró TELEGRAM_BOT_TOKEN en las variables de entorno.")
        sys.exit(1)

    print("🤖 Iniciando CyberGuardian Telegram Bot con soporte VirusTotal y Modo Heurístico...")
    try:
        asyncio.run(run_telegram_bot())
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Bot de Telegram detenido por el usuario.")
