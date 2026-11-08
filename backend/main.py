import os
import sys
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory of backend to sys.path if running this file directly
# to ensure absolute imports (backend.database...) work seamlessly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import engine, Base
from backend.api.routes.analysis import router as analysis_router

# Configure logging system
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("cyberguardian")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación FastAPI:
    1. Inicializa las tablas de la base de datos en el arranque (startup).
    2. Inicia el bot de Telegram en una tarea asíncrona en segundo plano sin bloquear el servidor.
    3. Detiene y cancela limpiamente la tarea del bot al apagar el servidor (shutdown)
       para evitar fugas de memoria o sockets colgados.
    """
    logger.info("Initializing database tables on startup...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize database tables: {str(e)}", exc_info=True)

    # Iniciar bot de Telegram en segundo plano de manera desacoplada y no bloqueante
    telegram_bot = None
    bot_task: Optional[asyncio.Task] = None

    try:
        from backend.telegram_bot import CyberGuardianTelegramBot
        telegram_bot = CyberGuardianTelegramBot()
        app.state.telegram_bot = telegram_bot

        if telegram_bot.is_configured:
            logger.info("Iniciando bot de Telegram en segundo plano...")
            bot_task = asyncio.create_task(
                telegram_bot.start_polling(), 
                name="cyberguardian_telegram_bot"
            )
            app.state.bot_task = bot_task
            logger.info("Tarea en segundo plano del bot de Telegram iniciada exitosamente.")
        else:
            logger.warning("TELEGRAM_BOT_TOKEN no configurado en .env. El bot de Telegram no se iniciará automáticamente.")
    except Exception as e:
        logger.error(f"No se pudo iniciar el bot de Telegram en segundo plano: {e}", exc_info=True)

    yield

    logger.info("Shutting down CyberGuardian API...")
    if telegram_bot:
        try:
            logger.info("Solicitando detención limpia del bot de Telegram...")
            telegram_bot.stop()
        except Exception as e:
            logger.warning(f"Error al solicitar detención de bot de Telegram: {e}")

    if bot_task and not bot_task.done():
        try:
            bot_task.cancel()
            try:
                await asyncio.wait_for(bot_task, timeout=3.0)
            except asyncio.CancelledError:
                pass
        except asyncio.TimeoutError:
            logger.warning("Timeout al esperar finalización de la tarea del bot de Telegram.")
        except Exception as e:
            logger.warning(f"Error al cancelar la tarea del bot de Telegram: {e}")

    logger.info("CyberGuardian API y servicios en segundo plano detenidos correctamente.")

# Initialize FastAPI application
app = FastAPI(
    title="CyberGuardian API",
    description="Plataforma anti-phishing y concientización ciudadana con orquestación multiagente.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS Middleware
# ALLOWED_ORIGINS: lista de orígenes separados por coma en .env
# Ejemplo producción: ALLOWED_ORIGINS=https://cyberguardian.app,https://www.cyberguardian.app
# Ejemplo desarrollo local: ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
# IMPORTANTE: No usar allow_origins=["*"] junto con allow_credentials=True
#             ya que los navegadores rechazan esa combinación (violación CORS spec).
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Global unhandled exception handler to return clean JSON error payloads
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception encountered at {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Ocurrió un error interno en el servidor. Por favor, intente de nuevo más tarde."
        }
    )

# Include routes router under prefix '/api'
app.include_router(analysis_router, prefix="/api", tags=["Analysis"])

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    load_dotenv()
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    logger.info(f"Starting server on http://{host}:{port}")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True, log_level=log_level)
