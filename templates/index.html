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

    # Cross-Platform Anti-Block Headless Configuration
    ydl_opts = {
        'format': 'bestaudio/best' if download_type == 'audio' else 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'youtube_include_dash_manifest': False,
        'youtube_include_hls_manifest': False,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'tvhtml5'],
                'skip': ['webpage', 'authcheck']
            },
            'tiktok': {
                'app_version': '34.0.0',
                'manifest_version': '1'
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://tiktok.com' if 'tiktok.com' in video_url else 'https://instagram.com',
            'Referer': 'https://tiktok.com/' if 'tiktok.com' in video_url else 'https://instagram.com/'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            direct_url = info_dict.get('url')
            
            # Format extractor for nested nodes
            if not direct_url and 'formats' in info_dict:
                valid_formats = [f for f in info_dict['formats'] if f.get('url') and f.get('vcodec') != 'none']
                if not valid_formats:
                    valid_formats = [f for f in info_dict['formats'] if f.get('url')]
                if valid_formats:
                    direct_url = valid_formats[-1]['url']

            if not direct_url:
                return jsonify({'error': 'Could not parse media data link. Platform restricted public server access.'}), 500

            title = "".join([c for c in info_dict.get('title', 'video') if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            ext = 'mp3' if download_type == 'audio' else 'mp4'
            
            return jsonify({
                'success': True,
                'download_url': direct_url,
                'filename': f"{title}.{ext}"
            })

    except Exception as e:
        return jsonify({'error': f"Platform Security Error: Server IP is temporarily throttled by this specific app network. Details: {str(e)}"}), 500

application = app
