import yt_dlp
import requests
import re
from typing import Optional, Dict

class VideoExtractor:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}

    def identify_platform(self, url: str) -> str:
        u = url.lower()
        if 'shopee' in u or 'shp.ee' in u: return 'shopee'
        if 'tiktok.com' in u: return 'tiktok'
        if 'instagram.com' in u: return 'instagram'
        return 'unknown'

    def extract_shopee_video(self, url: str) -> Optional[Dict]:
        try:
            res = requests.get(url, headers=self.headers, allow_redirects=True, timeout=15)
            video_match = re.search(r'https://cv\.shopee\.com\.br/file/[a-zA-Z0-9]+', res.text)
            if video_match:
                return {'video_url': video_match.group(0), 'title': 'Produto Shopee'}
            return None
        except: return None

    def extract_social_video(self, url: str) -> Optional[Dict]:
        try:
            ydl_opts = {'format': 'best', 'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {'video_url': info.get('url'), 'title': info.get('title', 'Vídeo Social')}
        except: return None
