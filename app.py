from flask import Flask, render_template, request, jsonify, Response
import yt_dlp
import requests

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
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            direct_url = info_dict.get('url')
            
            if not direct_url and 'formats' in info_dict:
                valid_formats = [f for f in info_dict['formats'] if f.get('url') and f.get('vcodec') != 'none']
                if not valid_formats:
                    valid_formats = [f for f in info_dict['formats'] if f.get('url')]
                if valid_formats:
                    direct_url = valid_formats[-1]['url']

            if not direct_url:
                return jsonify({'error': 'Platform block! Link parse nahi ho saka.'}), 500

            title = "".join([c for c in info_dict.get('title', 'video') if c.isalnum() or c==' ']).rstrip()
            ext = 'mp3' if download_type == 'audio' else 'mp4'
            filename = f"{title}.{ext}"
            
            # YAHAN SE PROXY TRIGGER HOGI: Direct frontend ko bhej rahe hain custom route par
            return jsonify({
                'success': True,
                'proxy_url': f"/stream?url={direct_url}&filename={filename}"
            })

    except Exception as e:
        return jsonify({'error': f"Server Throttled: {str(e)}"}), 500

# NAYA ROUTE: Jo video ko download karwayega mobile me direct play nahi hone dega
@app.route('/stream')
def stream_video():
    video_url = request.args.get('url')
    filename = request.args.get('filename', 'video.mp4')
    
    req = requests.get(video_url, stream=True)
    
    # Headers jo mobile browser ko force karenge file save karne par
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Content-Type': req.headers.get('Content-Type', 'video/mp4')
    }
    
    return Response(req.iter_content(chunk_size=1024*1024), headers=headers)

application = app
