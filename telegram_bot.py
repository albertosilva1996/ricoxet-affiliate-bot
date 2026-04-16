"""
Bot Telegram para Afiliados Shopee - Extrai vídeos, gera artes e hashtags
"""
import os
import logging
import re
import requests
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

# --- SERVIDOR WEB PARA MANTER ALIVE ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Online!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- IMPORTAÇÃO DOS SEUS MÓDULOS ---
from video_extractor import VideoExtractor
from image_generator import StoryImageGenerator
from hashtag_generator import HashtagGenerator

# Carregar variáveis
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Inicializar módulos
video_extractor = VideoExtractor()
image_generator = StoryImageGenerator()
hashtag_generator = HashtagGenerator()

class ShopeeAffiliateBot:
    def __init__(self, token: str):
        self.token = token
        self.app = Application.builder().token(token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("limpar", self.cleanup_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_link))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        welcome_message = "🎉 **Bem-vindo ao Bot de Afiliados Shopee!**\n\nEnvie um link para começar! 🚀"
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("📚 Envie um link da Shopee, TikTok ou Instagram.")

    async def cleanup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Corrigido para chamar a função correta de limpeza
        if hasattr(video_extractor, 'cleanup_temp_files'):
            video_extractor.cleanup_temp_files()
        await update.message.reply_text("✅ Arquivos temporários limpos!")

    async def handle_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        url = update.message.text.strip()
        if not url.startswith('http'):
            await update.message.reply_text("❌ Envie um link válido.")
            return
        
        processing_msg = await update.message.reply_text("⏳ Preparando seu kit de vendas... 🚀")
        
        try:
            platform = video_extractor.identify_platform(url)
            if platform == 'unknown':
                await processing_msg.edit_text("❌ Plataforma não reconhecida.")
                return

            # CORREÇÃO AQUI: Chamando a função exata que está no seu video_extractor.py
            product_data = video_extractor.extract_shopee_video(url)
            
            if not product_data:
                await processing_msg.edit_text("❌ Não consegui baixar os dados desse link.")
                return

            # Enviar Vídeo
            video_url = product_data.get('video_url')
            if video_url:
                await update.message.reply_video(video=video_url, caption="✅ Vídeo pronto!")

            # Gerar Arte e Legenda
            image_path = image_generator.generate_story_image(
                product_image_url=product_data.get('image_url', ''),
                product_name=product_data.get('title', 'Oferta'),
                current_price=product_data.get('price', 0),
                original_price=product_data.get('original_price', 0),
                affiliate_link="Link na Bio!"
            )

            content = hashtag_generator.generate_full_post(
                product_name=product_data.get('title', 'Produto'),
                current_price=product_data.get('price', 0),
                original_price=product_data.get('original_price', 0)
            )

            if image_path and Path(image_path).exists():
                with open(image_path, 'rb') as img_file:
                    await update.message.reply_photo(photo=img_file, caption="🎨 Sugestão Stories")

            await update.message.reply_text(
                f"📝 **LEGENDA:**\n\n{content['caption']}\n\n🚀 #tiktokcriador",
                parse_mode='Markdown'
            )
            await processing_msg.delete()

        except Exception as e:
            logger.error(f"Erro: {e}")
            await processing_msg.edit_text(f"❌ Erro ao processar: {str(e)}")

    def run(self):
        logger.info("🚀 Bot iniciado!")
        self.app.run_polling()

def main():
    # CORREÇÃO AQUI: Sincronizado com a KEY do seu Render
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("❌ TOKEN NÃO ENCONTRADO! Verifique as Environment Variables no Render.")
        return
    
    keep_alive() # Inicia o Flask para o Render não derrubar o bot
    bot = ShopeeAffiliateBot(token)
    bot.run()

if __name__ == '__main__':
    main()
    
