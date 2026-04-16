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
        elif 'instagram' in link or 'ig' in link:
            return 'instagram'
        return 'unknown'

    def extract_shopee_video(self, url: str) -> Optional[Dict]:
        try:
            session = requests.Session()
            # Força o redirecionamento para sair do br.shp.ee e ir para o link real
            res = session.get(url, headers=self.headers, allow_redirects=True, timeout=20)
            final_url = res.url
            
            # Se cair em Shopee Video, buscamos o link direto no HTML
            if 'sv.shopee.com.br' in final_url:
                video_url_match = re.search(r'https://cv\.shopee\.com\.br/[^?"]+', res.text)
                if video_url_match:
                    return {
                        'title': "Vídeo Shopee",
                        'price': 0, 
                        'original_price': 0,
                        'video_url': video_url_match.group(0),
                        'image_url': "" 
                    }

            # Se for produto, busca os IDs
            match = re.search(r'i\.(\d+)\.(\d+)', final_url) or re.search(r'product/(\d+)/(\d+)', final_url)
            
            if not match:
                logger.error(f"IDs não encontrados na URL: {final_url}")
                return None

            shop_id, item_id = match.groups()
            api_url = f"https://shopee.com.br/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
            api_res = session.get(api_url, headers=self.headers, timeout=20)
            data = api_res.json().get('data')

            if not data:
                return None

            video_info = data.get('video_info_list', [])
            return {
                'title': data.get('name'),
                'price': data.get('price') / 100000,
                'original_price': data.get('price_before_discount', 0) / 100000,
                'video_url': video_info[0].get('video_url') if video_info else None,
                'image_url': f"https://down-br.img.susercontent.com/file/{data.get('image')}"
            }
        except Exception as e:
            logger.error(f"Erro Shopee: {e}")
            return None
            
    
