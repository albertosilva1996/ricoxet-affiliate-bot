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
        """Identifica a plataforma do link incluindo links curtos"""
        link = url.lower()
        if 'shopee' in link or 'shp.ee' in link:
            return 'shopee'
        elif 'tiktok' in link:
            return 'tiktok'
        elif 'instagram' in link or 'ig' in link:
            return 'instagram'
        return 'unknown'
    
    def extract_shopee_video(self, url: str) -> Optional[Dict]:
        try:
            # Resolve o redirecionamento do link curto
            res = requests.get(url, headers=self.headers, allow_redirects=True, timeout=10)
            final_url = res.url
            
            # Busca os IDs no link final (grande)
            match = re.search(r'i\.(\d+)\.(\d+)', final_url)
            if not match:
                match = re.search(r'product/(\d+)/(\d+)', final_url)
            
            if not match:
                return None
                
            shop_id, item_id = match.groups()
            api_url = f"https://shopee.com.br/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
            api_res = requests.get(api_url, headers=self.headers, timeout=10)
            item = api_res.json().get('data')
            
            if not item: return None
            
            video_list = item.get('video_info_list', [])
            return {
                'title': item.get('name'),
                'price': item.get('price') / 100000,
                'original_price': item.get('price_before_discount') / 100000,
                'video_url': video_list[0].get('video_url') if video_list else None,
                'image_url': f"https://down-br.img.susercontent.com/file/{item.get('image')}"
            }
        except Exception as e:
            logger.error(f"Erro Shopee: {e}")
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
