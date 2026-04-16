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
        # Headers atualizados para parecer um navegador real
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://shopee.com.br/'
        }

    def identify_platform(self, url: str) -> str:
        """Identifica se o link é Shopee (curto ou longo), TikTok ou Insta"""
        link = url.lower()
        if 'shopee' in link or 'shp.ee' in link:
            return 'shopee'
        elif 'tiktok' in link:
            return 'tiktok'
        elif 'instagram' in link or 'ig.me' in link:
            return 'instagram'
        return 'unknown'

    def extract_shopee_video(self, url: str) -> Optional[Dict]:
        """Abre o link curto e extrai o vídeo e dados do produto"""
        try:
            # 1. Resolve o link curto (br.shp.ee) para o link real
            session = requests.Session()
            res = session.get(url, headers=self.headers, allow_redirects=True, timeout=15)
            final_url = res.url
            
            # 2. Busca o ID da Loja e do Item no link final
            # O padrão da Shopee é i.SHOPID.ITEMID
            match = re.search(r'i\.(\d+)\.(\d+)', final_url)
            if not match:
                # Tenta o padrão de URL de produto direto
                match = re.search(r'product/(\d+)/(\d+)', final_url)
            
            if not match:
                logger.error(f"Não foi possível localizar os IDs na URL: {final_url}")
                return None

            shop_id, item_id = match.groups()

            # 3. Faz a chamada na API da Shopee usando os IDs encontrados
            api_url = f"https://shopee.com.br/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
            api_res = session.get(api_url, headers=self.headers, timeout=15)
            data = api_res.json().get('data')

            if not data:
                logger.error("A API da Shopee não retornou dados para este item.")
                return None

            # 4. Localiza o vídeo (se disponível)
            video_url = None
            video_info = data.get('video_info_list', [])
            if video_info:
                video_url = video_info[0].get('video_url')

            return {
                'title': data.get('name'),
                'price': data.get('price') / 100000, # Shopee envia o preço com 5 zeros a mais
                'original_price': data.get('price_before_discount', 0) / 100000,
                'video_url': video_url,
                'image_url': f"https://down-br.img.susercontent.com/file/{data.get('image')}"
            }

        except Exception as e:
            logger.error(f"Erro ao extrair dados da Shopee: {e}")
            return None

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
