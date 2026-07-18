import os
import sys
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Ajuste dinámico de rutas para poder importar tu backend sin errores
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.agents.orchestrator import Orchestrator

# Cargar el .env para obtener TELEGRAM_BOT_TOKEN y GROQ_API_KEY
load_dotenv()

# Inicializamos tu IA central
orchestrator = Orchestrator()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde al comando /start."""
    welcome_text = (
        "🛡️ ¡Hola! Soy el bot de **CyberGuardian**.\n\n"
        "Envíame cualquier texto, correo sospechoso o enlace, y utilizaré IA para analizar su nivel de riesgo y detectar amenazas."
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def analyze_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe el texto del usuario, lo procesa con la IA y devuelve el reporte."""
    user_text = update.message.text
    
    # Mensaje temporal mientras la IA piensa
    processing_msg = await update.message.reply_text("🔍 Analizando contenido con el motor de IA...")
    
    try:
        # Llamamos a tu orquestador, pasándole "telegram" como fuente para la base de datos
        result = orchestrator.analyze(content=user_text, source="telegram")
        
        # Determinar el semáforo de riesgo
        risk_level = result.get('risk_level', 'UNKNOWN')
        emoji = "🔴" if risk_level == "CRITICAL" else "🟠" if risk_level == "HIGH" else "🟡" if risk_level == "MEDIUM" else "🟢"
        
        # Construir la respuesta final con Markdown
        response = f"🛡️ **Reporte de CyberGuardian**\n\n"
        response += f"{emoji} **Nivel de Riesgo:** {risk_level} ({result.get('risk_score', 0)}/100)\n\n"
        
        response += f"📖 **Explicación:**\n{result.get('educational_explanation', 'Sin explicación disponible.')}\n\n"
        
        findings = result.get('findings', [])
        if findings:
            response += "⚠️ **Hallazgos:**\n"
            for f in findings:
                response += f"- {f}\n"
            response += "\n"
            
        recommendations = result.get('recommendations', [])
        if recommendations:
            response += "✅ **Recomendaciones:**\n"
            for r in recommendations:
                response += f"- {r}\n"
                
        # Reemplazar el mensaje de "Analizando..." con el resultado final
        await processing_msg.edit_text(response, parse_mode='Markdown')
        
    except Exception as e:
        await processing_msg.edit_text(f"❌ Ocurrió un error al procesar la solicitud:\n`{str(e)}`", parse_mode='Markdown')

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ ERROR: No se encontró TELEGRAM_BOT_TOKEN en las variables de entorno.")
        sys.exit(1)
        
    # Construir la aplicación de Telegram
    app = ApplicationBuilder().token(token).build()
    
    # Agregar los manejadores de eventos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_message))
    
    print("🤖 Bot de Telegram iniciado exitosamente. Presiona CTRL+C para detener.")
    
    # Iniciar el bot (se queda escuchando en bucle)
    app.run_polling()