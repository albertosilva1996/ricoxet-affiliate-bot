"""
Bot Telegram para Afiliados Shopee - Extrai vídeos, gera artes e hashtags
"""
import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot Online!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# Chame isso antes de iniciar o bot
keep_alive()


from video_extractor import VideoExtractor
from image_generator import StoryImageGenerator
from hashtag_generator import HashtagGenerator

# Carregar variáveis de ambiente
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
    """Bot Telegram para Afiliados Shopee"""
    
    def __init__(self, token: str):
        self.token = token
        self.app = Application.builder().token(token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura os handlers do bot"""
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("limpar", self.cleanup_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_link))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /start"""
        welcome_message = """
🎉 **Bem-vindo ao Bot de Afiliados Shopee!**

Eu sou seu assistente para criar conteúdo viral de vendas. 

**O que eu faço:**
✅ Baixo vídeos sem marca d'água (Shopee, TikTok, Instagram)
✅ Gero artes prontas para Stories com preço e CTA
✅ Sugiro hashtags bombadas para o seu nicho
✅ Crio legendas persuasivas

**Como usar:**
1️⃣ Envie um link do produto (Shopee, TikTok ou Instagram)
2️⃣ Aguarde alguns segundos
3️⃣ Receba:
   - 📹 Vídeo sem marca d'água
   - 🎨 Imagem para Stories
   - 📝 Legenda + Hashtags

**Exemplo de link:**
`https://shopee.com.br/product-i.123456.789012`

Envie um link para começar! 🚀
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /help"""
        help_text = """
📚 **GUIA DE AJUDA**

**Comandos disponíveis:**
/start - Mostra mensagem de boas-vindas
/help - Mostra esta mensagem
/limpar - Limpa arquivos temporários

**Plataformas suportadas:**
🛍️ Shopee - Links de produtos
🎵 TikTok - Links de vídeos
📸 Instagram - Links de Reels

**Dicas:**
💡 Quanto melhor a foto do produto, melhor a arte gerada
💡 Produtos em promoção geram mais engajamento
💡 Use as hashtags sugeridas para aumentar alcance

**Problemas?**
Se o bot não conseguir processar um link, tente:
1. Verificar se o link está correto
2. Aguardar alguns segundos e tentar novamente
3. Usar /limpar para limpar cache

Envie um link para começar! 🚀
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def cleanup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para /limpar"""
        video_extractor.cleanup_temp_files()
        await update.message.reply_text("✅ Arquivos temporários limpos com sucesso!")
    
async def handle_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para links de produtos - CORRIGIDO E SEM ERROS"""
        url = update.message.text.strip()
        
        if not url.startswith('http'):
            await update.message.reply_text("❌ Isso não parece um link válido. Envie um link da Shopee, TikTok ou Instagram.")
            return
        
        processing_msg = await update.message.reply_text("⏳ Processando seu kit de vendas... Segura aí! 🚀")
        
        try:
            platform = video_extractor.identify_platform(url)
            
            if platform == 'unknown':
                await processing_msg.edit_text("❌ Plataforma não reconhecida. Use links da Shopee, TikTok ou Instagram.")
                return

            await processing_msg.edit_text(f"🔍 Extraindo conteúdo do {platform.upper()}...")
            product_data = video_extractor.extract_video(url)
            
            if not product_data:
                await processing_msg.edit_text("❌ Não consegui baixar os dados desse link. Tente outro!")
                return

            # Envio do Vídeo
            video_path = product_data.get('video_path')
            if video_path and Path(video_path).exists():
                await processing_msg.edit_text("📹 Enviando vídeo sem marca d'água...")
                with open(video_path, 'rb') as video_file:
                    await update.message.reply_video(video=video_file, caption="✅ Vídeo pronto!")

            # Geração de Arte e Legenda
            await processing_msg.edit_text("🎨 Criando arte e hashtags virais...")
            
            image_path = image_generator.generate_story_image(
                product_image_url=product_data.get('image_url', ''),
                product_name=product_data.get('title', 'Oferta do Dia'),
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
                    await update.message.reply_photo(
                        photo=img_file,
                        caption="🎨 **Sugestão para Stories**",
                        parse_mode='Markdown'
                    )

            await update.message.reply_text(
                f"📝 **LEGENDA PRONTA:**\n\n{content['caption']}\n\n"
                f"🚀 **HASHTAGS:**\n{ ' '.join(content['hashtags']) } #tiktokcriador",
                parse_mode='Markdown'
            )

            await processing_msg.delete()

        except Exception as e:
            logger.error(f"Erro geral: {e}")
            if processing_msg:
                try:
                    await processing_msg.edit_text("❌ Erro ao processar. Tente novamente em instantes.")
                except:
                    pass
    
    def run(self):
        """Inicia o bot"""
        logger.info("🚀 Bot iniciado!")
        self.app.run_polling()


def main():
    """Função principal"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ ERRO: TELEGRAM_BOT_TOKEN não configurado!")
        print("\nConfigure a variável de ambiente:")
        print("export TELEGRAM_BOT_TOKEN='seu_token_aqui'")
        return
    
    bot = ShopeeAffiliateBot(token)
    bot.run()


if __name__ == '__main__':
    main()
