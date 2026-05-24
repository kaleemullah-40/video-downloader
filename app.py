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

    # Mobile App client emulation to bypass the "Sign in to confirm you're not a bot" block
    ydl_opts = {
        # 'ios' aur 'android' extractor use karne se bot block bypass ho jata hai
        'format': 'bestaudio/best' if download_type == 'audio' else 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android'],
                'skip': ['webpage']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            direct_url = info_dict.get('url')
            title = "".join([c for c in info_dict.get('title', 'video') if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            ext = 'mp3' if download_type == 'audio' else 'mp4'
            
            return jsonify({
                'success': True,
                'download_url': direct_url,
                'filename': f"{title}.{ext}"
            })

    except Exception as e:
        # Agar phir bhi issue aaye to extract_flat try karein ga error return karne ke bajaye
        return jsonify({'error': f"YouTube Blocked Request. Error: {str(e)}"}), 500

application = app
