"""
Módulo gerador de imagens para Stories com layout de venda
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Optional, Tuple
import requests
from io import BytesIO
import textwrap

class StoryImageGenerator:
    """Gerador de imagens para Stories no estilo Shopee Afiliados"""
    
    # Dimensões padrão para Stories (Instagram/TikTok)
    WIDTH = 1080
    HEIGHT = 1920
    
    # Cores
    BLUE_BG = (173, 216, 230)  # Azul claro
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)
    DARK_YELLOW = (255, 200, 0)
    RED = (255, 0, 0)
    GRAY = (100, 100, 100)
    
    def __init__(self):
        self.output_dir = Path("/tmp/shopee_bot_images")
        self.output_dir.mkdir(exist_ok=True)
        
        # Tentar carregar fontes do sistema
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self._load_fonts()
    
    def _load_fonts(self):
        """Carrega fontes disponíveis no sistema"""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
        
        for path in font_paths:
            try:
                if Path(path).exists():
                    self.font_large = ImageFont.truetype(path, 80)
                    self.font_medium = ImageFont.truetype(path, 60)
                    self.font_small = ImageFont.truetype(path, 40)
                    break
            except:
                pass
        
        # Fallback para fonte padrão
        if not self.font_large:
            self.font_large = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
    
    def download_image(self, image_url: str) -> Optional[Image.Image]:
        """Baixa uma imagem de URL"""
        try:
            response = requests.get(image_url, timeout=10)
            return Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"Erro ao baixar imagem: {e}")
            return None
    
    def resize_image_to_fit(self, img: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """Redimensiona imagem mantendo proporção"""
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        return img
    
    def format_price(self, price: float) -> str:
        """Formata preço em reais"""
        return f"R$ {price:.2f}".replace('.', ',')
    
    def generate_story_image(
        self,
        product_image_url: str,
        product_name: str,
        current_price: float,
        original_price: float,
        affiliate_link: str = "s.shopee.com.br"
    ) -> Optional[str]:
        """
        Gera imagem para Story com layout de venda
        
        Args:
            product_image_url: URL da imagem do produto
            product_name: Nome do produto
            current_price: Preço atual (com desconto)
            original_price: Preço original
            affiliate_link: Link de afiliado
        
        Returns:
            Caminho do arquivo gerado ou None
        """
        try:
            # Criar imagem base com fundo azul
            img = Image.new('RGB', (self.WIDTH, self.HEIGHT), self.BLUE_BG)
            draw = ImageDraw.Draw(img)
            
            # Baixar e redimensionar imagem do produto
            product_img = self.download_image(product_image_url)
            if product_img:
                product_img = self.resize_image_to_fit(product_img, 700, 900)
                # Criar card branco para a imagem
                card_width = 800
                card_height = 1000
                card_x = (self.WIDTH - card_width) // 2
                card_y = 150
                
                # Desenhar card branco com bordas arredondadas
                draw.rounded_rectangle(
                    [(card_x, card_y), (card_x + card_width, card_y + card_height)],
                    radius=30,
                    fill=self.WHITE
                )
                
                # Colar imagem do produto no card
                img_x = card_x + (card_width - product_img.width) // 2
                img_y = card_y + 50
                img.paste(product_img, (img_x, img_y))
            
            # Adicionar nome do produto
            product_name_wrapped = textwrap.fill(product_name, width=25)
            draw.text(
                (self.WIDTH // 2, 1150),
                product_name_wrapped,
                fill=self.BLACK,
                font=self.font_medium,
                anchor="mm"
            )
            
            # Adicionar preço original (riscado)
            original_price_text = self.format_price(original_price)
            draw.text(
                (self.WIDTH // 2 - 150, 1300),
                original_price_text,
                fill=self.RED,
                font=self.font_small,
                anchor="mm"
            )
            # Riscar o preço original
            bbox = draw.textbbox((self.WIDTH // 2 - 150, 1300), original_price_text, font=self.font_small)
            draw.line([(bbox[0], (bbox[1] + bbox[3]) // 2), (bbox[2], (bbox[1] + bbox[3]) // 2)], fill=self.RED, width=3)
            
            # Adicionar preço promocional em destaque
            current_price_text = self.format_price(current_price)
            
            # Caixa preta para o preço promocional
            price_box_width = 600
            price_box_height = 150
            price_box_x = (self.WIDTH - price_box_width) // 2
            price_box_y = 1380
            
            draw.rounded_rectangle(
                [(price_box_x, price_box_y), (price_box_x + price_box_width, price_box_y + price_box_height)],
                radius=20,
                fill=self.BLACK
            )
            
            draw.text(
                (self.WIDTH // 2, price_box_y + price_box_height // 2),
                current_price_text,
                fill=self.YELLOW,
                font=self.font_large,
                anchor="mm"
            )
            
            # Adicionar botão "Clique abaixo para comprar"
            button_y = 1600
            button_width = 700
            button_height = 120
            button_x = (self.WIDTH - button_width) // 2
            
            draw.rounded_rectangle(
                [(button_x, button_y), (button_x + button_width, button_y + button_height)],
                radius=20,
                fill=self.BLACK
            )
            
            draw.text(
                (self.WIDTH // 2, button_y + button_height // 2),
                "Clique abaixo 👇\npara comprar",
                fill=self.WHITE,
                font=self.font_small,
                anchor="mm",
                align="center"
            )
            
            # Adicionar emoji de dedo apontando
            draw.text(
                (150, 1700),
                "👉",
                font=self.font_large
            )
            
            # Adicionar link do afiliado
            draw.rounded_rectangle(
                [(100, 1800), (self.WIDTH - 100, 1880)],
                radius=15,
                fill=self.WHITE
            )
            
            draw.text(
                (self.WIDTH // 2, 1840),
                f"🛍️ {affiliate_link}",
                fill=self.BLACK,
                font=self.font_small,
                anchor="mm"
            )
            
            # Salvar imagem
            output_path = self.output_dir / f"story_{hash(product_name) % 100000}.png"
            img.save(output_path, quality=95)
            
            return str(output_path)
        
        except Exception as e:
            print(f"Erro ao gerar imagem: {e}")
            return None


if __name__ == "__main__":
    generator = StoryImageGenerator()
    
    # Teste com dados fictícios
    result = generator.generate_story_image(
        product_image_url="https://via.placeholder.com/500x500",
        product_name="Tênis Esportivo Confortável Academia",
        current_price=59.90,
        original_price=89.00,
        affiliate_link="s.shopee.com.br"
    )
    print(f"Imagem gerada: {result}")
