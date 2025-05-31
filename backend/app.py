from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests
import os
import time
import json
from urllib.parse import urlparse
from downloaders.youtube import get_youtube_info
# from downloaders.instagram import get_instagram_video_info
# from downloaders.facebook import get_facebook_video_info
# from downloaders.twitter import get_twitter_info
# from downloaders.tiktok import get_tiktok_info
# from downloaders.otherPlatforms import get_others_info
from asgiref.wsgi import WsgiToAsgi
app = Flask(__name__)
CORS(app)  # Allow requests from React frontend

@app.route("/api/get_video_info", methods=["POST"])
def get_video_info():
    data = request.get_json()
    url = data.get("url")
    platform = data.get("platform")

    if not url or not platform:
        return jsonify({"error": "Missing url or platform"}), 400

    try:
        match platform:
            case "youtube":
                info = get_youtube_info(url)
            case "instagram":
                info = get_youtube_info( url)
            case "facebook":
                info = get_youtube_info(url)
            case "twitter":
                info = get_youtube_info(url)
            case "tiktok":
                info = get_youtube_info(url)
            case "snapchat":
                info = get_youtube_info(url)
            case "pinterest":
                info = get_youtube_info(url)
            case _:
                 return jsonify({"error": "Unsupported platform"}), 500

        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# playwright install

@app.route('/api/download')


def download():
    url = request.args.get('url')
    if not url:
        return {"error": "No URL provided"}, 400

    # Platform-specific headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'identity',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    domain = urlparse(url).netloc.lower()
    platform = domain.split('.')[-2] if domain.count('.') >= 2 else domain
    
    # Platform-specific configurations
    if 'youtube.com' in domain or 'googlevideo.com' in domain:
        headers.update({
            'Origin': 'https://www.youtube.com',
            'Referer': 'https://www.youtube.com/',
            'Sec-Fetch-Dest': 'video',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
            'Range': 'bytes=0-',
        })
    elif 'instagram.com' in domain:
        headers.update({
            'Referer': 'https://www.instagram.com/',
            'Origin': 'https://www.instagram.com',
            'Sec-Fetch-Dest': 'video',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })
    elif 'snapchat.com' in domain or 'sc-cdn.net' in domain:
        headers.update({
            'Origin': 'https://www.snapchat.com',
            'Referer': 'https://www.snapchat.com/',
            'Sec-Fetch-Dest': 'video',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
        })
    elif 'tiktok.com' in domain or 'tiktokv.com' in domain:
        # Clean up TikTok URL parameters
        base_url = url.split('?')[0] if '?' in url else url
        params = {'a': '1988', '_': str(int(time.time()))}
        url = f"{base_url}?{'&'.join(f'{k}={v}' for k,v in params.items())}"
        
        headers.update({
            'Referer': 'https://www.tiktok.com/',
            'Origin': 'https://www.tiktok.com',
            'Authority': urlparse(url).netloc,
            'Sec-Fetch-Dest': 'video',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'cross-site',
            'Range': 'bytes=0-',
            'Cookie': 'tt_webid=1; tt_csrf_token=1',
        })
    else:
        # Default headers for other platforms
        headers.update({
            'Referer': f'https://{domain}',
            'Origin': f'https://{domain}',
        })

    try:
        # First verify the URL
        test = requests.head(url, headers=headers, allow_redirects=True, timeout=10)
        
        # Platform-specific retry logic
        if test.status_code != 200:
            if 'instagram.com' in domain:
                # Instagram often requires cookies
                headers['Cookie'] = 'ig_did=1; ig_nrcb=1'
                test = requests.head(url, headers=headers, allow_redirects=True, timeout=10)
            elif 'googlevideo.com' in domain:
                headers.pop('Range', None)
                test = requests.head(url, headers=headers, allow_redirects=True, timeout=10)
            
            if test.status_code != 200:
                return {"error": f"URL returned {test.status_code}", "platform": platform}, 400
        
        # Generate filename
        filename = f"{platform}_video_{int(time.time())}.mp4"
        if 'content-disposition' in test.headers:
            cd = test.headers['content-disposition']
            filename = cd.split('filename=')[1].strip('"\'') if 'filename=' in cd else filename
        
        # Stream the download with platform-specific timeout
        timeout = 45 if 'tiktok' in domain else 30
        r = requests.get(url, headers=headers, stream=True, timeout=timeout)
        
        # Handle redirects
        if r.status_code == 302:
            redirect_url = r.headers.get('Location')
            if redirect_url:
                r = requests.get(redirect_url, headers=headers, stream=True, timeout=timeout)
        
        if r.status_code != 200:
            return {"error": f"Download failed with status {r.status_code}", "platform": platform}, 400
        
        return Response(
            r.iter_content(chunk_size=8192),
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': r.headers.get('Content-Type', 'video/mp4'),
                'Cache-Control': 'no-store, max-age=0',
                'Platform': platform,
            }
        )
    
    except requests.exceptions.Timeout:
        return {"error": "Request timed out", "platform": platform}, 504
    except requests.exceptions.TooManyRedirects:
        return {"error": "Too many redirects", "platform": platform}, 400
    except Exception as e:
        return {"error": str(e), "platform": platform}, 500

# Path to analytics.json
ANALYTICS_FILE = os.path.join(os.path.dirname(__file__), 'analytics.json')

@app.route('/api/update-analytics', methods=['POST'])
def update_analytics():
    try:
        data = request.get_json()
        
        with open(ANALYTICS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        
        return jsonify({'message': 'Analytics updated successfully', 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/get-analytics', methods=['GET'])
def get_analytics():
    try:
        with open(ANALYTICS_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
    
asgi_app = WsgiToAsgi(app)
