import yt_dlp
import requests
from urllib.parse import urlparse
import time

def get_others_info(url, cookies_file='cookies.txt'):
    """Universal video extractor with improved Reddit and Pinterest support"""
    
    domain = urlparse(url).netloc.lower()
    platform = domain.split('.')[-2]
    
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forcejson': True,
        'format': 'best[ext=mp4]',
        'referer': url,
        'cookiefile': cookies_file,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
        },
        'extractor_args': {
            'tiktok': {'format': 'download_addr'},
            'instagram': {'format': 'video_url'},
            'reddit': {'format': 'fallback'},
            'pinterest': {'format': 'original'},
        },
    }

    # Platform-specific optimizations
    if 'snapchat.com' in domain:
        ydl_opts.update({
            'extract_flat': False,
            'ignoreerrors': True,
            'format': 'best[protocol^=https]',
            'http_headers': {
                **ydl_opts['http_headers'],
                'Origin': 'https://www.snapchat.com',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
            }
        })
    elif 'pinterest.' in domain:
        ydl_opts.update({
            'extract_flat': False,  # Changed from True
            'force_generic_extractor': False,  # Changed from True
            'format': 'best[ext=mp4]',
            'extractor_args': {
                'pinterest': {
                    'format': 'original',
                    'force_generic': False
                }
            }
        })
    elif 'reddit.com' in domain:
        ydl_opts.update({
        'quiet': True,
        'skip_download': True,
        'forcejson': True,
        'format': 'bestvideo[height<=1080]+bestaudio/best',
        'referer': 'https://www.reddit.com/',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Origin': 'https://www.reddit.com',
        },
        'extractor_args': {
            'reddit': {
                'fallback': True,
                'video_preference': 'dash'
            }
        }
    })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Enhanced URL extraction with verification
            download_url = None
            
            # Special handling for Reddit
            if 'reddit.com' in domain:
                if info.get('url'):
                    download_url = info['url']
                elif info.get('requested_formats'):
                    # Prefer DASH format for Reddit
                    for fmt in info['requested_formats']:
                        if fmt.get('ext') == 'mp4':
                            download_url = fmt['url']
                            break
            
            # Special handling for Pinterest
            elif 'pinterest.' in domain:
                if info.get('url'):
                    download_url = info['url']
                elif info.get('formats'):
                    # Look for original quality
                    for fmt in info['formats']:
                        if fmt.get('format_note', '').lower() == 'original':
                            download_url = fmt['url']
                            break
            
            # Generic fallback for other platforms
            if not download_url:
                if info.get('url'):
                    download_url = info['url']
                elif info.get('formats'):
                    formats = sorted(
                        [f for f in info['formats'] if f.get('url') and f.get('ext') == 'mp4'],
                        key=lambda x: (x.get('height', 0), x.get('width', 0), x.get('tbr', 0)),
                        reverse=True
                    )
                    if formats:
                        download_url = formats[0]['url']
            
            # Special URL processing
            if download_url:
                if 'tiktok.' in domain:
                    if 'playwm' in download_url:
                        download_url = download_url.replace('playwm', 'play')
                    download_url = f"{download_url}&_={int(time.time())}"
                elif 'reddit.com' in domain and 'v.redd.it' in download_url:
                    if not download_url.endswith('.mp4'):
                        download_url += '/DASH_720.mp4'  # Force specific quality
            
            # Verify thumbnail URL
            thumbnail = info.get("thumbnail")
            if not thumbnail and info.get("thumbnails"):
                thumbnail = next(
                    (t['url'] for t in info['thumbnails'] 
                    if t.get('url') and t['url'].startswith('http')),
                    None
                )
            
            return {
                "title": info.get("title") or info.get("description") or f"Video from {platform}",
                "thumbnail": thumbnail,
                "download_url": download_url,
                "platform": platform,
                "duration": info.get('duration'),
                "view_count": info.get('view_count'),
            }

    except Exception as e:
        return {
            "error": str(e),
            "platform": platform,
            "suggestion": "Try again with cookies if needed" if 'pinterest' in domain else "Try different URL format"
        }