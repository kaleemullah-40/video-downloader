from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url')
    download_type = request.form.get('type')
    
    if not video_url:
        return jsonify({'error': 'Please provide a valid URL'}), 400

    # Ultimate 2026 YouTube Bot-Block Bypass Configuration
    ydl_opts = {
        'format': 'bestaudio/best' if download_type == 'audio' else 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        # Yeh option direct player stream uthata hai aur main page bot verification bypass karta hai
        'youtube_include_dash_manifest': False,
        'youtube_include_hls_manifest': False,
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'mweb'],
                'skip': ['dash', 'hls']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Origin': 'https://www.youtube.com',
            'Referer': 'https://www.youtube.com/'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            
            # Agar format links list mein ho to direct url nikalna
            direct_url = info_dict.get('url')
            if not direct_url and 'formats' in info_dict:
                # Best quality format filter out karna
                valid_formats = [f for f in info_dict['formats'] if f.get('url')]
                if valid_formats:
                    direct_url = valid_formats[-1]['url']

            if not direct_url:
                return jsonify({'error': 'Could not extract direct stream URL. Try another video link.'}), 500

            title = "".join([c for c in info_dict.get('title', 'video') if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            ext = 'mp3' if download_type == 'audio' else 'mp4'
            
            return jsonify({
                'success': True,
                'download_url': direct_url,
                'filename': f"{title}.{ext}"
            })

    except Exception as e:
        # Fallback Mechanism: Agar main download fail ho to simple extractor try karein
        try:
            fallback_opts = {'quiet': True, 'skip_download': True, 'format': 'best'}
            with yt_dlp.YoutubeDL(fallback_opts) as ydl_fb:
                info_fb = ydl_fb.extract_info(video_url, download=False)
                return jsonify({
                    'success': True,
                    'download_url': info_fb.get('url') or info_fb['formats'][0]['url'],
                    'filename': "video.mp4"
                })
        except Exception as fallback_error:
            return jsonify({'error': f"YouTube Security Blocked Vercel Server. Details: {str(fallback_error)}"}), 500

application = app
