import yt_dlp
import requests
import re
import logging
from typing import Optional, Dict

class VideoExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }

    def identify_platform(self, url: str) -> str:
        url = url.lower()
        if 'shopee' in url or 'shp.ee' in url: return 'shopee'
        if 'tiktok.com' in url: return 'tiktok'
        if 'instagram.com' in url: return 'instagram'
        return 'unknown'

    def extract_shopee_video(self, url: str) -> Optional[Dict]:
        try:
            res = requests.get(url, headers=self.headers, allow_redirects=True, timeout=15)
            # Busca bruta por link de vídeo no HTML da Shopee
            video_match = re.search(r'https://cv\.shopee\.com\.br/file/[a-zA-Z0-9]+', res.text)
            if video_match:
                return {'video_url': video_match.group(0), 'title': 'Achadinho Shopee'}
            return None
        except: return None

    def extract_tiktok_video(self, url: str) -> Optional[Dict]:
        return self._universal_extract(url)

    def extract_instagram_video(self, url: str) -> Optional[Dict]:
        return self._universal_extract(url)

    def _universal_extract(self, url: str) -> Optional[Dict]:
        """Usa yt-dlp para extrair links diretos de TikTok e Instagram"""
        try:
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
                'force_generic_extractor': False,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'video_url': info.get('url'),
                    'title': info.get('title', 'Vídeo Social')
                }
        except Exception as e:
            logging.error(f"Erro universal: {e}")
            return None
            
