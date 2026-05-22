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

    # Vercel Serverless ke liye full memory-streaming configuration (Bina save kiye download hoga)
    ydl_opts = {
        'format': 'bestaudio/best' if download_type == 'audio' else 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': '-',  # Yeh option file ko disk par save karne ke bajaye standard output (memory) mein bhejta hai
        'logtostderr': True
    }

    try:
        def generate():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Video direct stream karne ke liye process create karna
                info_dict = ydl.extract_info(video_url, download=False)
                filename = ydl.prepare_filename(info_dict)
                ext = 'mp3' if download_type == 'audio' else 'mp4'
                clean_name = "".join([c for c in info_dict.get('title', 'video') if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                
                # Streaming header metadata setup
                headers = {
                    'Content-Disposition': f'attachment; filename="{clean_name}.{ext}"',
                    'Content-Type': 'audio/mpeg' if download_type == 'audio' else 'video/mp4'
                }
                
                # File stream generator ko return karna
                with ydl.urlopen(info_dict['url']) as stream:
                    while True:
                        chunk = stream.read(1024 * 256)  # 256KB chunks mein download stream
                        if not chunk:
                            break
                        yield chunk

        # Browser ko direct data block transfer karna bagair server crash kiye
        ext = 'mp3' if download_type == 'audio' else 'mp4'
        return Response(generate(), mimetype='audio/mpeg' if download_type == 'audio' else 'video/mp4', headers={'Content-Disposition': f'attachment; filename="download.{ext}"'})

    except Exception as e:
        return f"Vercel Streaming Error: {str(e)}", 500

