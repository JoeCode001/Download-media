import yt_dlp

def get_facebook_video_info(url):
    ydl_opts = {
    'quiet': True,
    'skip_download': True,
    'forcejson': True,
    'format': 'best',  # Try to get the best available quality
    'referer': url,    # Sometimes needed for Facebook
    'cookiefile': 'cookies.txt',
}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "download_url": info.get("url")
            }
    except Exception as e:
        return {"error": str(e)}
