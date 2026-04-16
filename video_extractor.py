"""
Módulo de extração de vídeos de múltiplas plataformas (Shopee, TikTok, Instagram)
"""
import requests
import re
import logging
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class VideoExtractor:
    def __init__(self):
        self.temp_dir = Path("/tmp/shopee_bot_videos")
        self.temp_dir.mkdir(exist_ok=True)
        # Headers mais robustos para evitar bloqueio
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://shopee.com.br/'
        }

    def identify_platform(self, url: str) -> str:
        link = url.lower()
        if 'shopee' in link or 'shp.ee' in link:
            return 'shopee'
        elif 'tiktok' in link:
            return 'tiktok'
        elif 'instagram' in link or 'ig.me' in link:
            return 'instagram'
        return 'unknown'

    def extract_shopee_video(self, url: str) -> Optional[Dict]:
        try:
            # 1. Cria uma sessão para manter os cookies
            session = requests.Session()
            session.headers.update(self.headers)

            # 2. Segue o link curto até virar o link grande
            res = session.get(url, allow_redirects=True, timeout=15)
            final_url = res.url
            logger.info(f"URL Resolvida: {final_url}")

            # 3. Busca os IDs (shopid e itemid) com um padrão mais forte
            # Procura por números após o 'i.' ou na estrutura de 'product/'
            match = re.search(r'i\.(\d+)\.(\d+)', final_url)
            if not match:
                match = re.search(r'product/(\d+)/(\d+)', final_url)
            
            if not match:
                logger.error("Não foi possível localizar os IDs do produto no link.")
                return None

            shop_id, item_id = match.groups()

            # 4. Chama a API de detalhes do item
            api_url = f"https://shopee.com.br/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
            api_res = session.get(api_url, timeout=15)
            data = api_res.json().get('data')

            if not data:
                logger.error("API da Shopee não retornou dados.")
                return None

            # 5. Pega o vídeo e a imagem (usando o ID da imagem principal)
            video_list = data.get('video_info_list', [])
            image_id = data.get('image')
            
            return {
                'title': data.get('name'),
                'price': data.get('price') / 100000,
                'original_price': data.get('price_before_discount', 0) / 100000,
                'video_url': video_list[0].get('video_url') if video_list else None,
                'image_url': f"https://down-br.img.susercontent.com/file/{image_id}" if image_id else None
            }

        except Exception as e:
            logger.error(f"Erro crítico na extração: {e}")
            return None
    
    def extract_tiktok_video(self, url: str) -> Optional[Dict]:
        """
        Extrai vídeo do TikTok usando yt-dlp
        Retorna: {video_path, title}
        """
        try:
            video_file = self.TEMP_DIR / f"tiktok_{hash(url) % 10000}.mp4"
            
            # Usar yt-dlp para baixar sem marca d'água
            cmd = [
                'yt-dlp',
                '-f', 'best',
                '-o', str(video_file),
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            if result.returncode == 0 and video_file.exists():
                return {
                    'video_path': str(video_file),
                    'title': 'Vídeo TikTok',
                    'platform': 'tiktok'
                }
        
        except Exception as e:
            print(f"Erro ao extrair vídeo TikTok: {e}")
        
        return None
    
    def extract_instagram_video(self, url: str) -> Optional[Dict]:
        """
        Extrai vídeo do Instagram usando yt-dlp
        Retorna: {video_path, title}
        """
        try:
            video_file = self.TEMP_DIR / f"instagram_{hash(url) % 10000}.mp4"
            
            cmd = [
                'yt-dlp',
                '-f', 'best',
                '-o', str(video_file),
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            if result.returncode == 0 and video_file.exists():
                return {
                    'video_path': str(video_file),
                    'title': 'Vídeo Instagram',
                    'platform': 'instagram'
                }
        
        except Exception as e:
            print(f"Erro ao extrair vídeo Instagram: {e}")
        
        return None
    
    def extract_video(self, url: str) -> Optional[Dict]:
        """
        Extrai vídeo de qualquer plataforma suportada
        """
        platform = self.identify_platform(url)
        
        if platform == 'shopee':
            return self.extract_shopee_video(url)
        elif platform == 'tiktok':
            return self.extract_tiktok_video(url)
        elif platform == 'instagram':
            return self.extract_instagram_video(url)
        
        return None
    
    def cleanup_temp_files(self):
        """Limpa arquivos temporários"""
        try:
            for file in self.TEMP_DIR.glob('*'):
                file.unlink()
        except Exception as e:
            print(f"Erro ao limpar arquivos temporários: {e}")


if __name__ == "__main__":
    extractor = VideoExtractor()
    
    # Teste com uma URL fictícia
    test_url = "https://shopee.com.br/product-i.123456.789012"
    result = extractor.extract_video(test_url)
    print(f"Resultado: {result}")
