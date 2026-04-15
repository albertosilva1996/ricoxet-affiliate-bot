"""
Módulo de extração de vídeos de múltiplas plataformas (Shopee, TikTok, Instagram)
"""
import os
import re
import requests
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

class VideoExtractor:
    """Extrator de vídeos sem marca d'água de múltiplas plataformas"""
    
    TEMP_DIR = Path("/tmp/shopee_bot_videos")
    
    def __init__(self):
        self.TEMP_DIR.mkdir(exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def identify_platform(self, url: str) -> str:
        """Identifica a plataforma do link"""
        if 'shopee' in url.lower():
            return 'shopee'
        elif 'tiktok' in url.lower():
            return 'tiktok'
        elif 'instagram' in url.lower() or 'ig' in url.lower():
            return 'instagram'
        return 'unknown'
    
    def extract_shopee_video(self, url: str) -> Optional[Dict]:
        """
        Extrai informações de vídeo da Shopee
        Retorna: {video_url, title, price, original_price, image_url}
        """
        try:
            # Extrair shop_id e item_id da URL
            match = re.search(r'i\.(\d+)\.(\d+)', url)
            if not match:
                return None
            
            item_id, shop_id = match.groups()
            
            # Chamar API interna da Shopee
            api_url = f"https://shopee.com.br/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
            response = requests.get(api_url, headers=self.headers, timeout=10)
            data = response.json()
            
            if data.get('error'):
                return None
            
            item_data = data.get('data', {})
            
            # Extrair informações do produto
            product_info = {
                'title': item_data.get('name', 'Produto'),
                'price': item_data.get('price', 0) / 100000,  # Shopee retorna em unidades pequenas
                'original_price': item_data.get('price_before_discount', 0) / 100000,
                'image_url': item_data.get('image', ''),
                'video_url': None,
                'platform': 'shopee'
            }
            
            # Tentar extrair vídeo
            video_list = item_data.get('video_info_list', [])
            if video_list:
                video_id = video_list[0].get('video_id')
                if video_id:
                    # Construir URL do vídeo via CDN da Shopee
                    product_info['video_url'] = f"https://cv.shopee.com.br/api/v4/video/get_video_url?video_id={video_id}"
            
            return product_info
        
        except Exception as e:
            print(f"Erro ao extrair vídeo Shopee: {e}")
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
