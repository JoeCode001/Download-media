import yt_dlp
import requests
import json
import time
from urllib.parse import urlparse, parse_qs

def get_tiktok_info(url, retries=3, cookies_file=None):
    """Reliable TikTok downloader with proper response handling"""
    
    def clean_response(data):
        """Handle TikTok's scrambled responses"""
        if isinstance(data, bytes):
            try:
                # Try UTF-8 decoding first
                return data.decode('utf-8')
            except UnicodeDecodeError:
                # Fallback to error-tolerant decoding
                return data.decode('utf-8', errors='replace')
        return data

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.tiktok.com/',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }

    try:
        # First try with yt-dlp
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best[ext=mp4]',
            'http_headers': headers,
            'extractor_args': {'tiktok': {'format': 'download_addr'}},
            'cookiefile': cookies_file,
            'ignore_no_formats_error': True,
            'force_generic_extractor': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info and info.get('url'):
                # Verify the URL is clean
                if isinstance(info['url'], str) and info['url'].startswith('http'):
                    return {
                        "status": "success",
                        "url": info['url'],
                        "info": {
                            "title": info.get('title', 'TikTok Video'),
                            "author": info.get('uploader', ''),
                            "duration": info.get('duration', 0),
                            "thumbnail": info.get('thumbnail', ''),
                        },
                        "method": "yt-dlp"
                    }

        # Fallback to direct page scraping
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        page_content = clean_response(response.text)
        
        # Look for JSON data in page
        json_start = page_content.find('"video":{"downloadAddr":"') + 24
        if json_start > 24:
            json_end = page_content.find('"', json_start)
            video_url = page_content[json_start:json_end].replace('\\u0026', '&')
            
            if video_url.startswith('http'):
                return {
                    "status": "success",
                    "url": video_url,
                    "info": {
                        "title": "TikTok Video",
                        "author": "",
                        "duration": 0,
                        "thumbnail": "",
                    },
                    "method": "page_scrape"
                }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "suggestion": "Try again with cookies"
        }

    return {
        "status": "error",
        "message": "Failed to extract video URL",
        "suggestion": "Try a different URL or method"
    }