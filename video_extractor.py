import requests
import re
import logging
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class VideoExtractor:
    def __init__(self):
        # Pasta temporária para salvar vídeos
        self.temp_dir = Path("/tmp/shopee_videos")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Cabeçalhos para o bot parecer um navegador real
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def identify_platform(self, url: str) -> str:
        """Identifica a plataforma do link"""
        link = url.lower()
        if 'shopee' in link or 'shp.ee' in link:
            return 'shopee'
        elif 'tiktok' in link:
            return 'tiktok'
        elif 'instagram' in link or 'ig' in link:
            return 'instagram'
        return 'unknown'

    def extract_video(self, url: str) -> Optional[Dict]:
        """Lógica principal para Shopee (Links curtos, Produtos e Vídeos)"""
        try:
            session = requests.Session()
            # 1. Resolve o redirecionamento (de br.shp.ee para o link real)
            res = session.get(url, headers=self.headers, allow_redirects=True, timeout=20)
            final_url = res.url
            
            # 2. Se cair na página de 'Shopee Video' (sv.shopee.com.br)
            if 'sv.shopee.com.br' in final_url:
                # Procura o link do vídeo bruto (cv.shopee.com.br) no código da página
                video_url_match = re.search(r'https://cv\.shopee\.com\.br/[^?"]+', res.text)
                if video_url_match:
                    return {
                        'title': "Vídeo Shopee",
                        'price': 0, 
                        'original_price': 0,
                        'video_url': video_url_match.group(0),
                        'image_url': "" 
                    }

            # 3. Se for um link de Produto normal, busca os IDs
            match = re.search(r'i\.(\d+)\.(\d+)', final_url) or re.search(r'product/(\d+)/(\d+)', final_url)
            
            if not match:
                logger.error(f"Não encontrei IDs na URL final: {final_url}")
                return None

            shop_id, item_id = match.groups()
            
            # 4. Consulta a API oficial da Shopee
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
            logger.error(f"Erro na extração Shopee: {e}")
            return None
                             
