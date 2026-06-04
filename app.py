from flask import Flask, render_template, request, jsonify, Response
import yt_dlp
import os
import urllib.request
import urllib.parse
import io

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

    # SOLUTION: Instead of passing a file, we load cookies as an in-memory string object
    if os.path.exists('cookies.txt'):
        try:
            with open('cookies.txt', 'r', encoding='utf-8') as f:
                cookie_content = f.read()
            
            # String stream loads without touching Vercel's read-only hard drive
            cookie_stream = io.StringIO(cookie_content)
            ydl_opts['cookiefile'] = cookie_stream
            ydl_opts['cookiefile_lock'] = False
        except Exception:
            pass # Fallback if file read fails

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
                return jsonify({'error': 'Platform block! Layout parameters changed or cookies out of sync.'}), 500

            title = "".join([c for c in info_dict.get('title', 'video') if c.isalnum() or c==' ']).rstrip()
            ext = 'mp3' if download_type == 'audio' else 'mp4'
            filename = f"{title}.{ext}"
            
            return jsonify({
                'success': True,
                'stream_url': f"/stream_file?url={urllib.parse.quote(direct_url)}&filename={urllib.parse.quote(filename)}"
            })

    except Exception as e:
        return jsonify({'error': f"Platform Update Error: {str(e)}"}), 500

# SECURE IN-MEMORY STREAM SYSTEM
@app.route('/stream_file')
def stream_file():
    target_url = request.args.get('url')
    filename = request.args.get('filename', 'video.mp4')
    
    req = urllib.request.Request(
        target_url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    
    def generate():
        with urllib.request.urlopen(req) as response:
            while True:
                chunk = response.read(1024 * 256) # 256KB Chunks
                if not chunk:
                    break
                yield chunk
                
    return Response(
        generate(),
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'video/mp4' if filename.endswith('.mp4') else 'audio/mpeg'
        }
    )

application = app
