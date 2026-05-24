from flask import Flask, render_template, request, Response
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form.get('url')
    download_type = request.form.get('type')  # 'video' or 'audio'
    
    if not video_url:
        return "Please provide a valid URL", 400

    # YouTube Block Bypass Settings (Bina crash ke downloading chalegi)
    ydl_opts = {
        'format': 'bestaudio/best' if download_type == 'audio' else 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': '-',  # Direct stream data to memory
        'logtostderr': True,
        # ANTI-BAN HEADERS (YouTube block nahi karega)
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Mode': 'navigate'
        }
    }

    try:
        def generate():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=False)
                
                # Title clean karna file download name ke liye
                clean_name = "".join([c for c in info_dict.get('title', 'video') if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                ext = 'mp3' if download_type == 'audio' else 'mp4'
                
                # Direct streaming from source URL chunks
                with ydl.urlopen(info_dict['url']) as stream:
                    while True:
                        chunk = stream.read(1024 * 512)  # 512KB fast download blocks
                        if not chunk:
                            break
                        yield chunk

        ext = 'mp3' if download_type == 'audio' else 'mp4'
        return Response(generate(), mimetype='audio/mpeg' if download_type == 'audio' else 'video/mp4', headers={'Content-Disposition': f'attachment; filename="download.{ext}"'})

    except Exception as e:
        return f"Download Failed: YouTube Security Blocked the Server. Details: {str(e)}", 500

application = app
