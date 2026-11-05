
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai 

# Si tienes el token de BotFather de Telegram, sustitúyelo entre las comillas
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "TU_TELEGRAM_BOT_TOKEN_AQUI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AQ.Ab8RN6JbC_9zhnLfPYYSFxjVwRjidlcaFSokZfXqZU4G2tdvvw")

client = genai.Client(api_key=GEMINI_API_KEY)

TIPSTER_SYSTEM_PROMPT = (
    "Eres el analista y tipster deportivo más preciso y riguroso del mundo. "
    "Tu tarea es realizar análisis deportivos exhaustivos y cuantitativos en tiempo real "
    "antes de emitir cualquier pronóstico o recomendación de valor.\n\n"
    "METODOLOGÍA DE ANÁLISIS EN TIEMPO REAL (Usa Google Search activamente):\n"
    "1. Factores de equipo: Estado de forma reciente, rachas (local/visitante), goles a favor/en contra esperados (xG), historial directo (H2H).\n"
    "2. Factores de plantilla: Bajas confirmadas, dudas de última hora, suspensiones, rotaciones tácticas y estilo del entrenador.\n"
    "3. Ventajas y condiciones de cuenta del usuario:\n"
    "   - Ventaja de sustituto: Si un jugador seleccionado es sustituido antes de cumplir un hito o según condiciones de la casa, tenlo en cuenta para mercados de jugadores.\n"
    "   - Garantía de dos goles: Pago anticipado si el equipo elegido saca 2 goles de ventaja en cualquier momento.\n"
    "4. Cobertura completa de mercados: Evalúa 1X2, hándicaps asiáticos/europeos, líneas de goles (over/under), ambos marcan (BTTS), corners, tarjetas y mercados especiales de rendimiento individual.\n"
    "5. Detección de valor: Compara la probabilidad real estimada contra el riesgo del mercado. "
    "Desglosa siempre tu pronóstico principal, una alternativa de menor riesgo y una opción de cuota alta bien fundamentada con datos recientes."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        " **Analista Tipster Pro activado**.\n\n"
        "Escríbeme el partido, evento o mercado que deseas que analice a fondo en tiempo real con datos actualizados."
    )

async def analyze_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=query,
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],
                system_instruction=TIPSTER_SYSTEM_PROMPT
            ),
        )

        reply_text = response.text if response.text else "No se obtuvo respuesta para el análisis."
        
        # Telegram tiene un límite de 4096 caracteres por mensaje
        if len(reply_text) > 4000:
            for i in range(0, len(reply_text), 4000):
                await update.message.reply_text(reply_text[i:i+4000])
        else:
            await update.message.reply_text(reply_text)

    except Exception as e:
        await update.message.reply_text(f"Error procesando el pronóstico: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), analyze_bet))
    print("Bot tipster en marcha...")
    app.run_polling()

