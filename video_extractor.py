"""
Módulo de extração de vídeos de múltiplas plataformas (Shopee, TikTok, Instagram)
"""
import requests
import re
import logging
import subprocess  # Corrigido: Faltava importar
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class VideoExtractor:
    def __init__(self):
        # Corrigido: Padronizado para minúsculo para bater com o resto do código
        self.temp_dir = Path("/tmp/shopee_bot_videos")
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
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
        """Extrai informações da Shopee resolvendo links curtos (br.shp.ee)"""
        try:
            res = requests.get(url, headers=self.headers, allow_redirects=True, timeout=15)
            final_url = res.url

            match = re.search(r'i\.(\d+)\.(\d+)', final_url)
            if not match:
                match = re.search(r'product/(\d+)/(\d+)', final_url)
            
            if not match:
                logger.error(f"Não encontrei IDs na URL final: {final_url}")
                return None

            shop_id, item_id = match.groups()

            api_url = f"https://shopee.com.br/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
            api_res = requests.get(api_url, headers=self.headers, timeout=15)
            item_data = api_res.json().get('data')

            if not item_data:
                return None

            video_list = item_data.get('video_info_list', [])
            return {
                'title': item_data.get('name'),
                'price': item_data.get('price') / 100000,
                'original_price': item_data.get('price_before_discount', 0) / 100000,
                'video_url': video_list[0].get('video_url') if video_list else None,
                'image_url': f"https://down-br.img.susercontent.com/file/{item_data.get('image')}"
            }

        except Exception as e:
            logger.error(f"Erro na extração Shopee: {e}")
            return None
    
    def extract_tiktok_video(self, url: str) -> Optional[Dict]:
        try:
            video_file = self.temp_dir / f"tiktok_{hash(url) % 10000}.mp4"
            cmd = ['yt-dlp', '-f', 'best', '-o', str(video_file), url]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            if result.returncode == 0 and video_file.exists():
                return {
                    'video_path': str(video_file),
                    'title': 'Vídeo TikTok',
                    'platform': 'tiktok'
                }
        except Exception as e:
            logger.error(f"Erro ao extrair vídeo TikTok: {e}")
        return None
    
    def extract_instagram_video(self, url: str) -> Optional[Dict]:
        try:
            video_file = self.temp_dir / f"instagram_{hash(url) % 10000}.mp4"
            cmd = ['yt-dlp', '-f', 'best', '-o', str(video_file), url]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            if result.returncode == 0 and video_file.exists():
                return {
                    'video_path': str(video_file),
                    'title': 'Vídeo Instagram',
                    'platform': 'instagram'
                }
        except Exception as e:
            logger.error(f"Erro ao extrair vídeo Instagram: {e}")
        return None
    
    def extract_video(self, url: str) -> Optional[Dict]:
        platform = self.identify_platform(url)
        if platform == 'shopee':
            return self.extract_shopee_video(url)
        elif platform == 'tiktok':
            return self.extract_tiktok_video(url)
        elif platform == 'instagram':
            return self.extract_instagram_video(url)
        return None
    
    def cleanup_temp_files(self):
        try:
            for file in self.temp_dir.glob('*'):
                file.unlink()
        except Exception as e:
            logger.error(f"Erro ao limpar arquivos: {e}")
