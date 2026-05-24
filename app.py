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

    ydl_opts = {
        'format': 'bestaudio/best' if download_type == 'audio' else 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Sirf video ka data link extract karein bina download kiye
            info_dict = ydl.extract_info(video_url, download=False)
            direct_url = info_dict.get('url')
            title = "".join([c for c in info_dict.get('title', 'video') if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            ext = 'mp3' if download_type == 'audio' else 'mp4'
            
            # Frontend browser ko direct video url aur details bhejien
            return jsonify({
                'success': True,
                'download_url': direct_url,
                'filename': f"{title}.{ext}"
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

application = app
