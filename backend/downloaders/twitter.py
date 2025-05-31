import yt_dlp

def get_twitter_info(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': 'best[ext=mp4]/best',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title", "Twitter Video"),
            "thumbnail": info.get("thumbnail"),
            "download_url": info.get("url"),
            "info": {
                            "title": info.get('title', 'Twitter Video'),
                            "author": info.get('uploader', ''),
                            "duration": info.get('duration', 0),
                            "thumbnail": info.get('thumbnail', ''),
                        },
        }
