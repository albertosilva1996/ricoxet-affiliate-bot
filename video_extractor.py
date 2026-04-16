import requests
import re
import logging
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class VideoExtractor:
    def __init__(self):
        self.temp_dir = Path("/tmp/shopee_videos")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Headers atualizados para evitar bloqueios
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://shopee.com.br/',
            'Connection': 'keep-alive'
        }

    def identify_platform(self, url: str) -> str:
        link = url.lower()
        if 'shopee' in link or 'shp.ee' in link:
            return 'shopee'
        if 'tiktok' in link:
            return 'tiktok'
        if 'instagram' in link or 'ig' in link:
            return 'instagram'
        return 'unknown'

    def extract_shopee_video(self, url: str) -> Optional[Dict]:
        """Lógica aprimorada para extração da Shopee"""
        try:
            session = requests.Session()
            # 1. Resolve redirecionamento com timeout maior
            res = session.get(url, headers=self.headers, allow_redirects=True, timeout=15)
            final_url = res.url
            
            # Se for link de VÍDEO (sv.shopee...)
            if 'sv.shopee.com.br' in final_url or '/events3/video' in final_url:
                video_match = re.search(r'https://cv\.shopee\.com\.br/[^?"]+', res.text)
                if video_match:
                    return {
                        'title': "Achadinho Shopee",
                        'price': 0,
                        'original_price': 0,
                        'video_url': video_match.group(0),
                        'image_url': ""
                    }

            # Se for link de PRODUTO (br.shp.ee ou produto direto)
            # Tenta pegar IDs via Regex de várias formas
            match = re.search(r'i\.(\d+)\.(\d+)', final_url) or re.search(r'product/(\d+)/(\d+)', final_url)
            
            if match:
                shop_id, item_id = match.groups()
                api_url = f"https://shopee.com.br/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
                api_res = session.get(api_url, headers=self.headers, timeout=10)
                data = api_res.json().get('data')
                
                if data:
                    video_info = data.get('video_info_list', [])
                    return {
                        'title': data.get('name', 'Produto Shopee'),
                        'price': data.get('price', 0) / 100000,
                        'original_price': data.get('price_before_discount', 0) / 100000,
                        'video_url': video_info[0].get('video_url') if video_info else None,
                        'image_url': f"https://down-br.img.susercontent.com/file/{data.get('image')}" if data.get('image') else ""
                    }

            # Se chegou aqui e não extraiu, tenta uma busca bruta por qualquer link de vídeo no HTML
            brute_video = re.search(r'https://cv\.shopee\.com\.br/file/[a-zA-Z0-9]+', res.text)
            if brute_video:
                return {
                    'title': "Vídeo Encontrado",
                    'price': 0, 'original_price': 0,
                    'video_url': brute_video.group(0),
                    'image_url': ""
                }

            return None
            
        except Exception as e:
            logger.error(f"Erro Shopee: {e}")
            return None

    def cleanup_temp_files(self):
        try:
            for file in self.temp_dir.glob("*"):
                file.unlink()
        except Exception as e:
            logger.error(f"Erro cleanup: {e}")
