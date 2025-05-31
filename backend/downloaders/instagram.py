import yt_dlp

def get_instagram_video_info(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forcejson': True,
        'format': 'best',
        'referer': url,
        # Instagram-specific options
        'cookiefile': 'cookies.txt',  # Recommended for private accounts
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Instagram often provides multiple formats
            download_url = info.get('url')
            if not download_url and 'formats' in info:
                # Get the best quality video URL
                for f in sorted(info['formats'], key=lambda x: x.get('height', 0), reverse=True):
                    if f.get('url'):
                        download_url = f['url']
                        break
            
            return {
                "title": info.get("title") or "Instagram Video",
                "thumbnail": info.get("thumbnail"),
                "info": {
                            "title": info.get('title', 'Instagram Video'),
                            "author": info.get('uploader', ''),
                            "duration": info.get('duration', 0),
                            "thumbnail": info.get('thumbnail', ''),
                        },
                "download_url": download_url,
            }
    except Exception as e:
        return {"error": str(e)}