# 🚀 Bot Telegram para Afiliados Shopee

Um bot inteligente que automatiza a criação de conteúdo para afiliados Shopee. Extrai vídeos sem marca d'água, gera artes para Stories e sugere hashtags bombadas.

## ✨ Funcionalidades

- **📹 Download de Vídeos**: Baixa vídeos sem marca d'água de:
  - Shopee (produtos)
  - TikTok
  - Instagram (Reels)

- **🎨 Geração de Artes**: Cria imagens profissionais para Stories com:
  - Foto do produto
  - Preço original (riscado)
  - Preço promocional em destaque
  - Botão de CTA ("Clique abaixo para comprar")
  - Emoji de dedo apontando
  - Link do afiliado

- **📝 Hashtags Inteligentes**: Gera hashtags relevantes por categoria:
  - Análise automática do produto
  - Hashtags genéricas de alta performance
  - Legendas persuasivas personalizadas

## 🛠️ Instalação

### Pré-requisitos

- Python 3.8+
- ffmpeg (para processamento de vídeos)
- pip

### Passo 1: Clonar ou baixar o projeto

```bash
cd ~/shopee_affiliate_bot
```

### Passo 2: Instalar dependências

```bash
pip install -r requirements.txt
```

### Passo 3: Configurar o Token do Bot

1. Abra o Telegram e procure por **@BotFather**
2. Envie `/newbot` e siga as instruções
3. Copie o token fornecido
4. Crie um arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
```

5. Edite o arquivo `.env` e adicione seu token:

```
TELEGRAM_BOT_TOKEN=seu_token_aqui
```

### Passo 4: Instalar ffmpeg (se necessário)

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Baixe em https://ffmpeg.org/download.html

## 🚀 Como Usar

### Iniciar o Bot

```bash
python telegram_bot.py
```

O bot começará a escutar mensagens no Telegram.

### Usar o Bot

1. **Abra o Telegram** e procure pelo seu bot (ou clique no link fornecido pelo BotFather)

2. **Envie um link** de produto:
   - Shopee: `https://shopee.com.br/product-i.123456.789012`
   - TikTok: `https://www.tiktok.com/@usuario/video/123456789`
   - Instagram: `https://www.instagram.com/p/ABC123DEF456/`

3. **Aguarde** alguns segundos enquanto o bot processa

4. **Receba**:
   - 📹 Vídeo sem marca d'água
   - 🎨 Imagem para Stories
   - 📝 Legenda + Hashtags

### Comandos Disponíveis

- `/start` - Mostra mensagem de boas-vindas
- `/help` - Mostra guia de ajuda
- `/limpar` - Limpa arquivos temporários

## 📊 Estrutura do Projeto

```
shopee_affiliate_bot/
├── telegram_bot.py          # Bot principal
├── video_extractor.py       # Extrator de vídeos
├── image_generator.py       # Gerador de artes
├── hashtag_generator.py     # Gerador de hashtags
├── requirements.txt         # Dependências
├── .env.example            # Exemplo de configuração
└── README.md               # Este arquivo
```

## 🌐 Deploy em Produção

### Opção 1: VPS (Recomendado)

1. **Alugar um VPS** (DigitalOcean, Linode, AWS, etc.)
2. **SSH para o servidor**:
   ```bash
   ssh root@seu_servidor
   ```
3. **Instalar dependências**:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip ffmpeg
   ```
4. **Clonar o projeto**:
   ```bash
   git clone seu_repositorio
   cd shopee_affiliate_bot
   pip install -r requirements.txt
   ```
5. **Configurar .env** com seu token
6. **Usar screen ou systemd** para manter o bot rodando:

   **Com screen:**
   ```bash
   screen -S bot_shopee
   python telegram_bot.py
   # Pressione Ctrl+A depois D para desanexar
   ```

   **Com systemd (melhor):**
   Crie `/etc/systemd/system/shopee-bot.service`:
   ```ini
   [Unit]
   Description=Shopee Affiliate Bot
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/shopee_affiliate_bot
   ExecStart=/usr/bin/python3 /home/ubuntu/shopee_affiliate_bot/telegram_bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   Ative com:
   ```bash
   sudo systemctl enable shopee-bot
   sudo systemctl start shopee-bot
   sudo systemctl status shopee-bot
   ```

### Opção 2: Render/Heroku (Mais fácil)

1. **Crie uma conta** em https://render.com ou https://www.heroku.com
2. **Conecte seu repositório Git**
3. **Configure variáveis de ambiente** (TELEGRAM_BOT_TOKEN)
4. **Deploy automático**

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'telegram'"

```bash
pip install python-telegram-bot
```

### "yt-dlp: command not found"

```bash
pip install yt-dlp
```

### "ffmpeg: command not found"

Instale ffmpeg conforme instruções acima.

### Bot não responde

1. Verifique se o token está correto no `.env`
2. Verifique a conexão com a internet
3. Veja os logs de erro no terminal

### Imagem não é gerada

- Verifique se a URL da imagem do produto é válida
- Tente usar `/limpar` para limpar cache
- Verifique se Pillow está instalado: `pip install Pillow`

## 📈 Dicas de Uso

### Para Máximo Engajamento

1. **Use produtos em promoção** - Geram mais interesse
2. **Escolha fotos de qualidade** - Melhor imagem = melhor arte
3. **Poste em horários de pico** - Terça a quinta, 19h-21h
4. **Use todas as hashtags** - Aumenta alcance exponencialmente
5. **Varie os produtos** - Não poste o mesmo 10x seguidas

### Categorias com Melhor Performance

- 👟 Tênis e calçados
- 👕 Roupas em geral
- 📱 Eletrônicos
- 💄 Beleza e cosméticos
- 🏠 Decoração e casa

## 🤝 Contribuições

Encontrou um bug? Tem uma sugestão? Abra uma issue ou PR!

## 📄 Licença

Este projeto é de uso livre para fins educacionais e comerciais.

## ⚠️ Aviso Legal

- Respeite os termos de serviço do Telegram e das plataformas
- Use apenas para fins legítimos de afiliação
- Não viole direitos autorais dos produtos
- Cumpra as políticas de cada plataforma

## 📞 Suporte

Dúvidas? Abra uma issue no repositório ou entre em contato!

---

**Desenvolvido com ❤️ para afiliados Shopee**
