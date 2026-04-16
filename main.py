import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from video_extractor import VideoExtractor

# Configuração de Logs
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

extractor = VideoExtractor()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    platform = extractor.identify_platform(url)
    
    if platform == 'unknown':
        return 

    await update.message.reply_text(f"🔍 Detectado: {platform.capitalize()}. Processando...")

    try:
        data = None
        if platform == 'shopee':
            data = extractor.extract_shopee_video(url)
        elif platform in ['tiktok', 'instagram']:
            data = extractor.extract_social_video(url)

        if data and data.get('video_url'):
            await update.message.reply_video(
                video=data['video_url'],
                caption=f"🎥 {data.get('title', 'Vídeo')}\n\n#afiliado #viral"
            )
        else:
            await update.message.reply_text("❌ Não consegui extrair o vídeo. O link pode estar protegido.")
            
    except Exception as e:
        await update.message.reply_text(f"⚠️ Erro técnico: {str(e)}")

if __name__ == '__main__':
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    application = ApplicationBuilder().token(token).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🚀 Bot iniciado!")
    application.run_polling()
